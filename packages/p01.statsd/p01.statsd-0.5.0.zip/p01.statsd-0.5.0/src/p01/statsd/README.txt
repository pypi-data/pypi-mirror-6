======
README
======

Statsd client and server implementation based on gevent.

  >>> import p01.statsd.server
  >>> import p01.statsd.client


server
------

Setup a server and replace the real backend with a fake backend which appends
the data to a list:

  >>> interface = '0.0.0.0:8125'
  >>> backend = '0.0.0.0:2003'
  >>> server = p01.statsd.server.StatsdServer(interface, backend)
  >>> server
  <StatsdServer ('0.0.0.0', 8125) -> ('0.0.0.0', 2003)>

As you can see, the server provides the following internals:

  >>> server._interface
  ('0.0.0.0', 8125)

  >>> server._backend
  <GraphiteBackend ('0.0.0.0', 2003)>

  >>> server._percent
  90.0

  >>> server._interval
  5.0

  >>> server._prefix
  ''

  >>> server._debug
  False
