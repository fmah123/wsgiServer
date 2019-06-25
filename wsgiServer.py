import socket
from io import StringIO
import sys

class WSGIServer(object):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue__size = 1

    def __init__(self, server_address):
        #Create a listen socket
        self.listening_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )

        #Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        #bind
        listen_socket.bind(server_address)
        #Activate
        listening_socket.listen(self.request_queue__size)
        #Get Server host name and port
        host, port = self.listening_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        #Return headers set by web frameworks/Web applications
        self.header_set = []

    def set_app(self, application):
        self.application = application


    def serve_forever(self):
        listen_socket = self.listening_socket
        while True:
            #New client connection
            self.client_connection, client_address = listening_socket.accept()
            #Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            self.handle_one_request()

    def handle_one_request(self):
        self.request_data = request_data = self.client_connection.recv(1024)
        #Print formatted request data a la 'curl -v'
        print(''.join(
            '<{line}\n'.format(line=line)
            for line in request_data.splitline()    
        ))           

        self.parse_request(request_data)

        #Construct environment dictonary using request data
        env = self.get_environ()

        #It's time to call out application callable and get back a result that will become a HTTP response body.
        result = self.application(env, self.start_response)

        #Construct a response and send it back to the client
        self.finish_response(result)
    
    def parse_request(self, text):
        request_line = text.splitlines()[0]
        # rstrip() removes whitespace and/or charater from end of string/text.
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (
            self.request_method,
            self.path,
            self.request_version
        )  = request_line.split() 

    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes 
        # to emphasize the required variables and their values 
        # 
        # Required WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        #sys.stderr is where any uncaught exception will be dumped and logged by web server 
        #https://www.python.org/dev/peps/pep-0333/#preface for reference
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        #require CGI variables
        env['wsgi.run_once'] = False
        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)
        return env

    def start_response(self, status, response_headers, exc_info=None):
        #exc_info is for debugging use/error handling
        #Add neccessary server headings
        server_headers = [
            ('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2')
        ]
        self.headers_set = [status, response_headers + server_headers]
        #To adhere to the wsgi spec have to add a 'Write' callable function --> ignore for now
        #return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.header_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in result:
                response += data

            #Print formatted response data a la 'curl -v'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()   
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()
        

SERVER_ADDRESS = (Host, PORT) = '', 8888

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Provide a WSGI application object as module:callable")
    app_path = sys.argv[1]
    module, application = app_path.split(":")
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)    
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()


