# coding: utf-8
# Copyright 2009 Alexandre Fiori
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

import struct
import asyncio
from asyncio_mongo.exceptions import ConnectionLostError
import asyncio_mongo._bson as bson
from asyncio_mongo.log import logger

_ONE = b"\x01\x00\x00\x00"
_ZERO = b"\x00\x00\x00\x00"

"""Low level connection to Mongo."""


class _MongoQuery(object):
    def    __init__(self, id, collection, limit):
        self.id = id
        self.limit = limit
        self.collection = collection
        self.documents = []
        self.future = asyncio.Future()


class MongoProtocol(asyncio.Protocol):
    def __init__(self):
        self.__id = 0
        self.__buffer = b""
        self.__queries = {}
        self.__datalen = None
        self.__response = 0
        self.__waiting_header = True
        self._pipelined_calls = set() # Set of all the pipelined calls.
        self.transport = None
        self._is_connected = False

    def connection_made(self, transport):
        self.transport = transport
        self._is_connected = True
        logger.log(logging.INFO, 'Mongo connection made with %')

    def connection_lost(self, exc):
        self._is_connected = False
        self.transport = None

        # Raise exception on all waiting futures.
        for f in self.__queries:
            f.set_exception(ConnectionLostError(exc))

        logger.log(logging.INFO, 'Mongo connection lost')

    def data_received(self, data):
        while self.__waiting_header:
            self.__buffer += data
            if len(self.__buffer) < 16:
                break

            # got full header, 16 bytes (or more)
            header, extra = self.__buffer[:16], self.__buffer[16:]
            self.__buffer = b""
            self.__waiting_header = False
            datalen, request, response, operation = struct.unpack("<iiii", header)
            self.__datalen = datalen - 16
            self.__response = response
            if extra:
                self.data_received(extra)
            break
        else:
            if self.__datalen is not None:
                data, extra = data[:self.__datalen], data[self.__datalen:]
                self.__datalen -= len(data)
            else:
                extra = b""

            self.__buffer += data
            if self.__datalen == 0:
                self.message_received(self.__response, self.__buffer)
                self.__datalen = None
                self.__waiting_header = True
                self.__buffer = b""
                if extra:
                    self.data_received(extra)

    def message_received(self, request_id, packet):
        # Response Flags:
        #   bit 0:    Cursor Not Found
        #   bit 1:    Query Failure
        #   bit 2:    Shard Config Stale
        #   bit 3:    Await Capable
        #   bit 4-31: Reserved
        QUERY_FAILURE = 1 << 1
        response_flag, cursor_id, start, length = struct.unpack("<iqii", packet[:20])
        if response_flag == QUERY_FAILURE:
            self.query_failure(request_id, cursor_id, response_flag,  bson.BSON(packet[20:]).decode())
            return
        self.query_success(request_id, cursor_id, bson.decode_all(packet[20:]))

    def send_message(self, operation, collection, message, query_opts=_ZERO):
        #print "sending %d to %s" % (operation, self)
        fullname = collection and bson._make_c_string(collection) or b""
        message = query_opts + fullname + message

        # 16 is the size of the header in bytes
        header = struct.pack("<iiii", 16 + len(message), self.__id, 0, operation)
        self.transport.write(header + message)
        self.__id += 1

    def OP_INSERT(self, collection, docs):
        docs = [bson.BSON.encode(doc) for doc in docs]
        self.send_message(2002, collection, b"".join(docs))

    def OP_UPDATE(self, collection, spec, document, upsert=False, multi=False):
        options = 0
        if upsert:
            options += 1
        if multi:
            options += 2

        message = struct.pack("<i", options) + \
            bson.BSON.encode(spec) + bson.BSON.encode(document)
        self.send_message(2001, collection, message)

    def OP_DELETE(self, collection, spec):
        self.send_message(2006, collection, _ZERO + bson.BSON.encode(spec))

    def OP_KILL_CURSORS(self, cursors):
        message = struct.pack("<i", len(cursors))
        for cursor_id in cursors:
            message += struct.pack("<q", cursor_id)
        self.send_message(2007, None, message)

    def OP_GET_MORE(self, collection, limit, cursor_id):
        message = struct.pack("<iq", limit, cursor_id)
        self.send_message(2005, collection, message)

    def OP_QUERY(self, collection, spec, skip, limit, fields=None):
        message = struct.pack("<ii", skip, limit) + bson.BSON.encode(spec)
        if fields:
            message += bson.BSON.encode(fields)

        query = _MongoQuery(self.__id, collection, limit)
        self.__queries[self.__id] = query
        self.send_message(2004, collection, message)
        return query.future

    def query_failure(self, request_id, cursor_id, response, raw_error):
        query = self.__queries.pop(request_id, None)
        if query:
            query.future.set_exception(ValueError("mongo error=%s" % repr(raw_error)))
            del query

    def query_success(self, request_id, cursor_id, documents):
        try:
            query = self.__queries.pop(request_id)
        except KeyError:
            return
        if isinstance(documents, list):
            query.documents += documents
        else:
            query.documents.append(documents)
        if cursor_id:
            query.id = self.__id
            next_batch = 0
            if query.limit:
                next_batch = query.limit - len(query.documents)
                # Assert, because according to the protocol spec and my observations
                # there should be no problems with this, but who knows? At least it will
                # be noticed, if something unexpected happens. And it is definitely
                # better, than silently returning a wrong number of documents
                assert next_batch >= 0, "Unexpected number of documents received!"
                if not next_batch:
                    self.OP_KILL_CURSORS([cursor_id])
                    query.future.set_result(query.documents)
                    return
            self.__queries[self.__id] = query
            self.OP_GET_MORE(query.collection, next_batch, cursor_id)
        else:
            query.future.set_result(query.documents)