======
README
======

This package offers a client and server for logging from pyhton application to
an elsticsearch server. The server is used as man in the middle and buffers
write access to one or more elasticsearch server. The client outputs it's
logging data in the json event format used by elasticsearch. This means the
server only needs to ship them to the elasticsearch server in  batches without
grok them.

  >>> import p01.kibana.server
  >>> import p01.kibana.client


server
------

Setup a server and replace the real backend with a fake backend which appends
the data to a list:

  >>> interface = '0.0.0.0:2200'
  >>> backend = '0.0.0.0:9200'
  >>> server = p01.kibana.server.KibanaServer(interface, backend)
  >>> server
  <KibanaServer ('0.0.0.0', 2200) -> ('0.0.0.0', 9200)>

As you can see, the server provides the following internals:

  >>> server._interface
  ('0.0.0.0', 2200)

  >>> server._backend
  <ElasticSearchBackend ('0.0.0.0', 9200)>

  >>> server._interval
  5.0

  >>> server._debug
  False
