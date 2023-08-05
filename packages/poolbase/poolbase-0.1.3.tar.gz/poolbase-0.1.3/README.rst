pypool
=====

a simple connection pool

expand pypool
~~~~~~~~~~~~~
must be implemented pypool.connection.Connection all method
a hbase extension like this:https://github.com/duanhongyi/hbase

Sample usage
~~~~~~~~~~~~

::

    from hbase import Connection
    pool = ConnectionPool(size,connection_klass=Connection,**{'host':'127.0.0.1','port':9090,})
    with pool.connection() as conn:
        //do something
        pass

Download
~~~~~~~~

* https://github.com/duanhongyi/pypool
