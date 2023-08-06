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
from asyncio_mongo._bson import SON

from asyncio_mongo._pymongo import helpers
from asyncio_mongo.collection import Collection
from asyncio import coroutine
from asyncio_mongo.exceptions import ErrorReply


class Database(object):
    def __init__(self, protocol, database_name):
        self.__protocol = protocol
        self._database_name = database_name

    def __str__(self):
        return self._database_name

    def __repr__(self):
        return "<mongodb Database: %s>" % self._database_name

    def __call__(self, database_name):
        return Database(self.__protocol, database_name)

    def __getitem__(self, collection_name):
        return Collection(self, collection_name)

    def __getattr__(self, collection_name):
        return self[collection_name]

    @property
    def _protocol(self):
        return self.__protocol

    @coroutine
    def create_collection(self, name, options=None):
        collection = Collection(self, name)

        if options:
            if "size" in options:
                options["size"] = float(options["size"])

            command = SON({"create": name})
            command.update(options)
            result = yield from self["$cmd"].find_one(command)
            if result.get("ok", 0.0):
                return collection
            else:
                raise RuntimeError(result.get("errmsg", "unknown error"))
        else:
            return collection

    @coroutine
    def drop_collection(self, name_or_collection):
        if isinstance(name_or_collection, Collection):
            name = name_or_collection._collection_name
        elif isinstance(name_or_collection, str):
            name = name_or_collection
        else:
            raise TypeError("name must be an instance of basestring or txmongo.Collection")

        return self["$cmd"].find_one({"drop": name})

    @coroutine
    def collection_names(self):
        results = yield from self["system.namespaces"].find()
        names = [r["name"] for r in results]
        names = [n[len(str(self)) + 1:] for n in names
                 if n.startswith(str(self) + ".")]
        names = [n for n in names if "$" not in n]
        return names

    @coroutine
    def authenticate(self, name, password):
        """
        Send an authentication command for this database.
        mostly stolen from asyncio_mongo._pymongo
        """
        if not isinstance(name, str):
            raise TypeError("name must be an instance of str")
        if not isinstance(password, str):
            raise TypeError("password must be an instance of str")

        # First get the nonce
        result = yield self["$cmd"].find_one({"getnonce": 1})
        return (yield self.authenticate_with_nonce(result, name, password))

    @coroutine
    def authenticate_with_nonce(self, result, name, password):
        nonce = result['nonce']
        key = helpers._auth_key(nonce, name, password)

        # hacky because order matters
        auth_command = SON(authenticate=1)
        auth_command['user'] = name
        auth_command['nonce'] = nonce
        auth_command['key'] = key

        # Now actually authenticate
        result = yield from self["$cmd"].find_one(auth_command)
        return self.authenticated(result)

    @coroutine
    def authenticated(self, result):
        """might want to just call callback with 0.0 instead of errback"""
        ok = result['ok']
        if ok:
            return ok
        else:
            raise ErrorReply(result['errmsg'])

