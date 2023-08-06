import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")



class Visualizer(object):
	def __init__(self):
		super(Visualizer, self).__init__()
		self.application = tornado.web.Application(
			[(r"/", MainHandler),]
		)
		self.application.listen(8000)
		tornado.ioloop.IOLoop.instance().start()
