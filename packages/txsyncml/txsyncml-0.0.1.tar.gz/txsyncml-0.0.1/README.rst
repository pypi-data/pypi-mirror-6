txsyncml
========

Limited SyncML 1.1 server.
Only implements the "Refresh sync from client only".

As per the docs (chapter 6.3)::

    The 'refresh sync from client only' is a synchronization type in
    which the client sends all its data from a database to the server
    (i.e., exports). The server is expected to replace all data in the
    target database with the data sent by the client. I.e., this means
    that the client overwrites all data in the server database.


Stages of a SyncML Session
--------------------------

- Pkg #1 client initialization package
- Pkg #2 server init package
- Pkg #3 client modification
- Pkg #4 server modifications
- Pkg #5 mapping of data ids
- Pkg #6 mapping status


An initialization package generally contains the following information:

- Device capabilities
- Requested databases access, type of sync desired
- Authentication information
- Sync anchors

A modification package generally contains the following information:

- Synchronization commands: add, replace, delete, move ...
- Data ids and contents associated with these commands (except for delete)

A mapping package (only sent by client) generally contains the following information:

- Mapping information (a couple of LUID and GUID for each new item added from server)


|travis|_ |coveralls|_


::

    $ virtualenv ve
    (ve)$ pip install -e .
    (ve)$ twistd txsyncml --help

.. |travis| image:: https://travis-ci.org/smn/txsyncml.png?branch=develop
.. _travis: https://travis-ci.org/smn/txsyncml

.. |coveralls| image:: https://coveralls.io/repos/smn/txsyncml/badge.png?branch=develop
.. _coveralls: https://coveralls.io/r/smn/txsyncml

