import SimpleHTTPServer
import SocketServer
import os

def serve(dir = "."):
	os.chdir(dir)

	PORT = int(os.getenv("PORT", 8080))

	Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

	print "serving at port", PORT
	httpd = SocketServer.TCPServer(("", PORT), Handler)

	httpd.serve_forever()
