=======
Asyncio Mongo
=======
:Info: See `the mongo site <http://www.mongodb.org>`_ for more information. See `Bitbucket <http://bitbucket.org/mrdon/asyncio-mongo>`_ for the latest source.
:Author: Don Brown<mrdon@twdata.org>

About
=====
An asynchronous Python driver for the Mongo database, based on Python's asyncio.
This project is based on `TxMongo <https://github.com/fiorix/mongo-async-python-driver>`_

This project is still in the very early alpha stage and shouldn't be used for production.

Docs and examples
=================
There are some examples in the *examples/* directory.

Features
========
- Works for the asyncio (PEP3156) event loop
- No dependencies
- Connection pooling

Missing
--------
- GridFS support

Credits
=======
Thanks to (in no particular order):

- Alexandre Fiori (fiorix)

  - The author of TxMongo

- Mike Dirolf (mdirolf)

  - The author of original ``pymongo`` package.

- Jonathan Slenders (jonathanslenders)
 
  - The author of asyncio_redis, from which the connection and pooling code come.

