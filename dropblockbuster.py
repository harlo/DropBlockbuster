import signal, json

import tornado.ioloop
import tornado.web
import tornado.httpserver

from time import sleep
from multiprocessing import Process
from sys import exit, argv

from api import DropBlockbusterAPI

def terminationHandler(signal, frame):
	exit(0)

signal.signal(signal.SIGINT, terminationHandler)

class DropBlockbuster(DropBlockbusterAPI, tornado.web.Application):
	def __init__(self):
		print "DropBlockbuster."

		try:
			with open(".config", 'rb') as config:
				self.config = json.loads(config.read())

			self.routes = [(r"/(js|css/[a-zA-Z0-9\-\._/]+)", self.AssetHandler,{ 'path' : self.config['asset_dir'] })]
		except Exception as e:
			raise Exception('could not launch from config:\n(%s) %s' % (type(e), e))

		self.routes.update([
			(r"/", self.MainHandler),
			(r"/videos", self.GetVideosHandler)])

	class MainHandler(tornado.web.RequestHandler):
		@tornado.web.asynchronous
		def get(self):
			print "hi"

	class GetVideosHandler(tornado.web.RequestHandler):
		@tornado.web.asynchronous
		def post(self):
			print "videos"

	class AssetHandler(tornado.web.StaticFileHandler):
		def get(self, path=None):
			print "PATH %s" % ("(none)" if path is None else path)

	def start_api_client(self):
		try:
			DropBlockbusterAPI.__init__(self)
		except Exception as e:
			raise Exception("could not start api client:\n(%s) %s" % (type(e), e))

	def start_web_client(self):
		tornado.web.Application.__init__(self, self.routes, **self.config['tornado_opts'])

		from api import start_daemon

		try:
			start_daemon(self.config['log_file'], self.config['pid_file'])

			server = tornado.httpserver.HTTPServer(self)
			server.bind(self.config['api_port'])
			server.start(self.config['num_processes'])

		except Exception as e:
			raise Exception("could not start web client:\n(%s) %s" % (type(e), e))

		tornado.ioloop.IOLoop.instance().start()

	def start(self):
		print "starting..."

		self.start_api_client()
		
		p = Process(target=self.start_web_client)
		p.start()

	def stop(self):
		print "stopping..."

		stop_daemon(self.config['pid_file'], with_ports=self.config['api_port'])

if __name__ == "__main__":
	if len(argv) != 2:
		print "usage: dropblockbuster.py -[start|stop|restart]"
		exit(-1)

	try:
		dropblockbuster = DropBlockbuster()
		
		if argv[1] in ["-stop", "-restart"]:
			dropblockbuster.stop()
			sleep(2)

		if argv[1] in ["-start", "-firstuse", "-restart"]:
			dropblockbuster.start()
	
	except Exception as e:
		print e
		exit(-1)

	exit(0)