"""
Base class for handling HTTP-POST request from Monit instances.

"""

__author__ = "Markus Juenemann <markus@juenemann.net"
__copyright__ = "Copyright (c) 2014 Markus Juenemann"
__license__ = "Simplified BSD License" 
__version__ = "1.0"
__vcs_id__ = "$Id:"


import socket
import BaseHTTPServer
import lxml.objectify
import constants


class MonitXmlHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def version_string(self):
        """
        Return the version string of the HTTP server.
        
        """
        
        return "nomit/%s" % (__version__)
    
    
    def finish(self,*args,**kw):
        """
        Re-write finish() to catch Broken Pipe errrors.
        http://stackoverflow.com/questions/6063416/python-basehttpserver-how-do-i-catch-trap-broken-pipe-errors
        
        """
        
        try:
            if not self.wfile.closed:
                self.wfile.flush()
                self.wfile.close()
          
        except socket.error:
            pass
          
        self.rfile.close()
        
        
    def log_message(self, fmt, *args):
        """
        Suppress logging of requests.
        
        """
        
        return


    def handle_unparsed(self, data):
        """
        Handle the unparsed XML data.
        
        This method is meant to be overriden. The default implementation 
        does nothing.
        
        :param data: Monit XML string.
        
        """
        
        pass
        
        


    def handle_parsed(self, monit):
        """
        Handle the parsed XML data.
        
        This method is meant to be overriden. The default implementation 
        does nothing.
        
        :param monit: Monit XML structure parsed by `lxml.objectify()`.
        
        """
        
        pass

    
    def do_POST(self):
        """
        Process HTTP-POST request from Monit instance. 
        
        """
        
        # Send 200/OK and headers.
        #
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        
        
        # Read all request data from client
        #
        data = self.rfile.read() 


        # Find the <monit>...</monit> section in the POST
        #
        try: 
            #start_pos = data.find("<monit")
            start_pos = data.find("<?xml")
            end_pos = data.find("</monit>")
            xml = data[start_pos:end_pos+len("</monit>")]
        except IndexError:
            return
        
        
        # Call the handler for unparsed XML
        #
        self.handle_unparsed(xml)

    
        # Parse XML into Python object hierarchy
        #
        monit = lxml.objectify.fromstring(xml)

                
        # Call the handler for parsed XML
        #
        self.handle_parsed(monit)
        

class _MonitDumpHandler(MonitXmlHandler):
    """
    Dump the `monit` structure for debugging purposes.
    
    """   
        
    def handle_unparsed(self, data):
        print xml.dom.minidom.parseString(data).toprettyxml(indent="  ")
        
    
    def handle_parsed(self, monit):
        print lxml.objectify.dump(monit)
        print "-" * 80

#
#
if __name__ == "__main__":
    
    import SocketServer as socketserver
    import BaseHTTPServer
    import xml.dom.minidom
    
    #server = socketserver.TCPServer(("127.0.0.1", 2811), _MonitDumpHandler)
    server = BaseHTTPServer.HTTPServer(("127.0.0.1", 2811), _MonitDumpHandler)
    server.serve_forever()
