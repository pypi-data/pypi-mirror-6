Nomit
=====

Nomit is a small library that can be used to process HTTP/XML POST
requests from Monit_ instances. While it is a relatively trivial adaption
of Python's `BaseHTTPRequestHandler`_, it may be useful to multiple 
other projects. For this reason Nomit is registered as its own little
project.

Monit_ is a free utility for managing Unix systems. Multiple Monit 
instances can be centrally managed by its sister project MMonit. 
Monit communicates with MMonit through HTTP/XML POST request.

Requirements
------------

Nomit uses the `lxml.objectify` module from the lxml_ project. Many Linux
distributions provide lxml_ in their native package format.

The `MonitHandler` class
------------------------

Nomit provides a single class `MonitHandler` which is a sub-class of
`BaseHTTPRequestHandler`_. `MonitHandler` is meant to be sub-classed
itself. 

It provides two methods:

- `handle_unparsed()` is called with the raw XML of the HTTP/XML POST request.
- `handle_parsed()` is called after the XML has been parsed by `lxml.objectify.fromstring()`.

The default implementation of these methods does nothing. Any derived class must
implement these methods as necessary.

Example
--------

The example below implements `handle_unparsed()` to print the raw XML as
POSTed by the Monit agent and uses `handle_parsed()` to display the data
structure returned by `lxml.objectify.fromstring()`::

    import BaseHTTPServer
    import xml.dom.minidom
    import lxml.objectify
    import nomit

    class ExampleHandler(nomit.MonitXmlHandler):
        def handle_unparsed(self, s):
            print xml.dom.minidom.parseString(s).toprettyxml()
        
        def handle_parsed(self, o):
            print lxml.objectify.dump(o)
            
    server = BaseHTTPServer.HTTPServer(("127.0.0.1", 2811), ExampleHandler)
    server.serve_forever()

Monit configuration
-------------------

The Monit agent must be told to POST status information to the Python
script above. From the agent's point of view the script is simply (another[1]_)
MMonit server.   

``monit.conf``:: 

    set mmonit http://monit:monit@mmonit.example.com:8080/collector 
               http://localhost:2811/
  
  
_[1] The ``set mmonit`` directive accepts multiple URLs.

.. _Monit: http://mmonit.com/monit/
.. _MMonit: http://mmonit.com/monit/#mmonit
.. _`BaseHTTPRequestHandler`: https://docs.python.org/2/library/basehttpserver.html
.. _lxml: http://lxml.de/