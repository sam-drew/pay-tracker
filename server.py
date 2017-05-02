import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.log import enable_pretty_logging
import logging
import os.path
from datetime import datetime

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

    def post(self):
        shiftStartDate = str(self.get_argument("shiftStartDate"))
        shiftStartTime = str(self.get_argument("shiftStartTime"))
        startDateTime = shiftStartDate + shiftStartTime
        startDateTime = datetime.strptime(startDateTime, '%Y-%m-%d%H:%M')

        shiftEndDate = str(self.get_argument("shiftEndDate"))
        shiftEndTime = str(self.get_argument("shiftEndTime"))
        endDateTime = shiftEndDate + shiftEndTime
        endDateTime = datetime.strptime(endDateTime, '%Y-%m-%d%H:%M')

        timeDelta = endDateTime - startDateTime
        tdDecimalHours = (timeDelta.seconds / 3600)
        breakLength = float(self.get_argument("breakLength"))
        paidHours = tdDecimalHours - breakLength
        self.redirect("/")

class SignUpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("signup.html")

enable_pretty_logging()
app = tornado.web.Application(
    [(r"/", RootHandler),(r"/signup", SignUpHandler),],
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    )

http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(8080)

tornado.ioloop.IOLoop.instance().start()
