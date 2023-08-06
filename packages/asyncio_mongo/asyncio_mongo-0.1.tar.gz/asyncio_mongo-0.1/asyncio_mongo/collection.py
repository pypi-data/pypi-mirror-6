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

from asyncio import coroutine
from asyncio_mongo import filter as qf
from asyncio_mongo._bson import SON, ObjectId, Code
from asyncio_mongo._pymongo import errors


class Collection(object):
    def __init__(self, database, name):
        if not isinstance(name, str):
            raise TypeError("name must be an instance of str")

        if not name or ".." in name:
            raise errors.InvalidName("collection names cannot be empty")
        if "$" in name and not (name.startswith("oplog.$main") or
                                name.startswith("$cmd")):
            raise errors.InvalidName("collection names must not "
                              "contain '$': %r" % name)
        if name[0] == "." or name[-1] == ".":
            raise errors.InvalidName("collection names must not start "
                              "or end with '.': %r" % name)
        if "\x00" in name:
            raise errors.InvalidName("collection names must not contain the "
                              "null character")

        self._database = database
        self._collection_name = name

    def __str__(self):
        return "%s.%s" % (str(self._database), self._collection_name)

    def __repr__(self):
        return "<mongodb Collection: %s>" % str(self)

    def __getitem__(self, collection_name):
        return Collection(self._database,
            "%s.%s" % (self._collection_name, collection_name))

    def __eq__(self, other):
        if isinstance(other, Collection):
            return (self._database, self._collection_name) == \
                       (other._database, other._collection_name)
        return NotImplemented

    def __hash__(self):
        return self._collection_name.__hash__()

    def __getattr__(self, collection_name):
        return self[collection_name]

    def __call__(self, collection_name):
        return self[collection_name]

    def _fields_list_to_dict(self, fields):
        """
        transform a list of fields from ["a", "b"] to {"a":1, "b":1}
        """
        as_dict = {}
        for field in fields:
            if not isinstance(field, str):
                raise TypeError("fields must be a list of key names")
            as_dict[field] = 1
        return as_dict

    def _gen_index_name(self, keys):
        return u"_".join([u"%s_%s" % item for item in keys])

    @coroutine
    def options(self):
        result = yield from self._database.system.namespaces.find_one({"name": str(self)})
        if result:
            options = result.get("options", {})
            if "create" in options:
                del options["create"]
            return options
        return {}

    @coroutine
    def find(self, spec=None, skip=0, limit=0, fields=None, filter=None, _proto=None):
        if spec is None:
            spec = SON()

        if not isinstance(spec, dict):
            raise TypeError("spec must be an instance of dict")
        if fields is not None and not isinstance(fields, (dict, list)):
            raise TypeError("fields must be an instance of dict or list")
        if not isinstance(skip, int):
            raise TypeError("skip must be an instance of int")
        if not isinstance(limit, int):
            raise TypeError("limit must be an instance of int")

        if fields is not None:
            if not isinstance(fields, dict):
                if not fields:
                    fields = ["_id"]
                fields = self._fields_list_to_dict(fields)

        if isinstance(filter, (qf.sort, qf.hint, qf.explain, qf.snapshot)):
            spec = SON(dict(query=spec))
            for k, v in filter.items():
                spec[k] = isinstance(v, tuple) and SON(v) or v

        # send the command through a specific connection
        # this is required for the connection pool to work
        # when safe=True
        if _proto is None:
            proto = self._database._protocol
        else:
            proto = _proto
        return (yield from proto.OP_QUERY(str(self), spec, skip, limit, fields))

    @coroutine
    def find_one(self, spec=None, fields=None, _proto=None):
        if isinstance(spec, ObjectId):
            spec = SON(dict(_id=spec))

        docs = yield from self.find(spec, limit=-1, fields=fields, _proto=_proto)
        doc = docs and docs[0] or {}
        if doc.get("err") is not None:
            if doc.get("code") == 11000:
                raise errors.DuplicateKeyError
            else:
                raise errors.OperationFailure(doc)
        else:
            return doc

    @coroutine
    def count(self, spec=None, fields=None):
        if fields is not None:
            if not fields:
                fields = ["_id"]
            fields = self._fields_list_to_dict(fields)

        spec = SON([("count", self._collection_name),
                    ("query", spec or SON()),
                    ("fields", fields)])
        result = yield from self._database["$cmd"].find_one(spec)
        return result["n"]

    @coroutine
    def group(self, keys, initial, reduce, condition=None, finalize=None):
        body = {
            "ns": self._collection_name,
            "key": self._fields_list_to_dict(keys),
            "initial": initial,
            "$reduce": Code(reduce),
        }

        if condition:
            body["cond"] = condition
        if finalize:
            body["finalize"] = Code(finalize)

        return (yield from self._database["$cmd"].find_one({"group": body}))

    @coroutine
    def filemd5(self, spec):
        if not isinstance(spec, ObjectId):
            raise ValueError(_("filemd5 expected an objectid for its "
                               "on-keyword argument"))

        spec = SON([("filemd5", spec),
                    ("root", self._collection_name)])

        result = yield from self._database['$cmd'].find_one(spec)
        return result.get('md5')

    @coroutine
    def __safe_operation(self, proto, safe=False, ids=None):
        callit = False
        result = None
        if safe is True:
            result = yield from self._database["$cmd"].find_one({"getlasterror": 1}, _proto=proto)
        else:
            callit = True

        if ids is not None:
            return ids

        if callit is True:
            return None
        
        return result

    @coroutine
    def insert(self, docs, safe=False):
        if isinstance(docs, dict):
            ids = docs.get('_id', ObjectId())
            docs["_id"] = ids
            docs = [docs]
        elif isinstance(docs, list):
            ids = []
            for doc in docs:
                if isinstance(doc, dict):
                    id = doc.get('_id', ObjectId())
                    ids.append(id)
                    doc["_id"] = id
                else:
                    raise TypeError("insert takes a document or a list of documents")
        else:
            raise TypeError("insert takes a document or a list of documents")
        proto = self._database._protocol
        proto.OP_INSERT(str(self), docs)
        result = yield from self.__safe_operation(proto, safe, ids)
        return result

    @coroutine
    def update(self, spec, document, upsert=False, multi=False, safe=False):
        if not isinstance(spec, dict):
            raise TypeError("spec must be an instance of dict")
        if not isinstance(document, dict):
            raise TypeError("document must be an instance of dict")
        if not isinstance(upsert, bool):
            raise TypeError("upsert must be an instance of bool")
        proto = self._database._protocol
        proto.OP_UPDATE(str(self), spec, document, upsert, multi)
        return (yield from self.__safe_operation(proto, safe))

    @coroutine
    def save(self, doc, safe=False):
        if not isinstance(doc, dict):
            raise TypeError("cannot save objects of type %s" % type(doc))

        objid = doc.get("_id")
        if objid:
            return (yield from self.update({"_id": objid}, doc, safe=safe, upsert=True))
        else:
            return (yield from self.insert(doc, safe=safe))

    @coroutine
    def remove(self, spec, safe=False):
        if isinstance(spec, ObjectId):
            spec = SON(dict(_id=spec))
        if not isinstance(spec, dict):
            raise TypeError("spec must be an instance of dict, not %s" % type(spec))

        proto = self._database._protocol
        proto.OP_DELETE(str(self), spec)
        return (yield from self.__safe_operation(proto, safe))

    @coroutine
    def drop(self, safe=False):
        return (yield from self.remove({}, safe))

    @coroutine
    def create_index(self, sort_fields, **kwargs):
        if not isinstance(sort_fields, qf.sort):
            raise TypeError("sort_fields must be an instance of filter.sort")

        if "name" not in kwargs:
            name = self._gen_index_name(sort_fields["orderby"])
        else:
            name = kwargs.pop("name")

        key = SON()
        for k,v in sort_fields["orderby"]:
            key.update({k:v})

        index = SON(dict(
          ns=str(self),
          name=name,
          key=key
        ))

        if "drop_dups" in kwargs:
            kwargs["dropDups"] = kwargs.pop("drop_dups")

        if "bucket_size" in kwargs:
            kwargs["bucketSize"] = kwargs.pop("bucket_size")
        
        index.update(kwargs)
        yield from self._database.system.indexes.insert(index, safe=True)
        return name

    @coroutine
    def ensure_index(self, sort_fields, **kwargs):
        # ensure_index is an alias of create_index since we are not 
        # keep an index cache same way pymongo does
        return (yield from self.create_index(sort_fields, **kwargs))

    @coroutine
    def drop_index(self, index_identifier):
        if isinstance(index_identifier, str):
            name = index_identifier
        elif isinstance(index_identifier, qf.sort):
            name = self._gen_index_name(index_identifier["orderby"])
        else:
            raise TypeError("index_identifier must be a name or instance of filter.sort")

        cmd = SON([("deleteIndexes", self._collection_name), ("index", name)])
        return (yield from self._database["$cmd"].find_one(cmd))

    @coroutine
    def drop_indexes(self):
        return (yield from self.drop_index("*"))

    @coroutine
    def index_information(self):
        raw = yield from self._database.system.indexes.find({"ns": str(self)})
        info = {}
        for idx in raw:
            info[idx["name"]] = idx["key"].items()
        return info

    @coroutine
    def rename(self, new_name):
        cmd = SON([("renameCollection", str(self)), ("to", "%s.%s" % \
            (str(self._database), new_name))])
        return (yield from self._database("admin")["$cmd"].find_one(cmd))

    @coroutine
    def distinct(self, key, spec=None):

        cmd = SON([("distinct", self._collection_name), ("key", key)])
        if spec:
            cmd["query"] = spec

        result = yield from self._database["$cmd"].find_one(cmd)
        if result:
            return result.get("values")
        return {}

    @coroutine
    def aggregate(self, pipeline, full_response=False):

        cmd = SON([("aggregate", self._collection_name),
                   ("pipeline", pipeline)])

        result = yield from self._database["$cmd"].find_one(cmd)
        if full_response:
            return result
        return result.get("result")

    @coroutine
    def map_reduce(self, map, reduce, full_response=False, **kwargs):

        cmd = SON([("mapreduce", self._collection_name), ("map", map), ("reduce", reduce)])
        cmd.update(**kwargs)
        result = yield from self._database["$cmd"].find_one(cmd)
        if full_response:
            return result
        return result.get("result")

    @coroutine
    def find_and_modify(self, query=None, update=None, upsert=False, **kwargs):
        if not update and not kwargs.get('remove', None):
            raise ValueError("Must either update or remove")

        if update and kwargs.get('remove', None):
            raise ValueError("Can't do both update and remove")

        cmd = SON([("findAndModify", self._collection_name)])
        cmd.update(kwargs)
        # No need to include empty args
        if query:
            cmd['query'] = query
        if update:
            cmd['update'] = update
        if upsert:
            cmd['upsert'] = upsert

        result = yield from self._database["$cmd"].find_one(cmd)
        no_obj_error = "No matching object found"
        if not result['ok']:
            if result["errmsg"] == no_obj_error:
                return None
            else:
                raise ValueError("Unexpected Error: %s" % (result,))
        return result.get('value')