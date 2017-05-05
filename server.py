import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.log import enable_pretty_logging
import logging
import os.path
from datetime import datetime
import bcrypt

# Class to define how to handle requests to the root of the website.
class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

# Class to define how to handle GET requests to "/calculate", and how to handle
# POST requests to made from the single shift calculator.
class CalculateHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("singleShift.html")

    def post(self):
        shiftStartDate = str(self.get_argument("shiftStartDate"))
        shiftStartTime = str(self.get_argument("shiftStartTime"))
        startDateTime = shiftStartDate + " " + shiftStartTime

        shiftEndDate = str(self.get_argument("shiftEndDate"))
        shiftEndTime = str(self.get_argument("shiftEndTime"))
        endDateTime = shiftEndDate + " " + shiftEndTime
        try:
            startDateTime = datetime.strptime(startDateTime, '%Y-%m-%d %H:%M')
            endDateTime = datetime.strptime(endDateTime, '%Y-%m-%d %H:%M')
        except:
            self.redirect("/calculate")

        timeDelta = endDateTime - startDateTime
        tdDecimalHours = (timeDelta.seconds / 3600)
        breakLength = float(self.get_argument("breakLength"))
        paidHours = tdDecimalHours - breakLength
        wage = float(self.get_argument("hourlyWage"))
        totalPay = (paidHours * wage)
        self.render("singleShiftResult.html", result = totalPay)

# Class to define how to handle requests made to the sign up page. Validate info
# is verified, and submit to database.
class SignUpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("signup.html", alerts = [])

    def post(self):
        info = []
        for argument in ["email1", "email2", "userPass1", "userPass2"]:
            info.append(self.get_argument(argument))
        logging.info("Attempt to add new user: {0}".format(info))
        alerts = []
        if self.get_argument("email1") != self.get_argument("email2"):
            alerts.append("Emails do not match")
            if self.get_argument("userPass1") != self.get_argument("userPass2"):
                alerts.append("Passwords do not match")
                logging.info("Failed to add new user; neither match")
                self.render("signup.html", alerts = alerts)
            else:
                self.render("signup.html", alerts = alerts)
                logging.info("Failed to add new user; emails don't match")
        elif self.get_argument("userPass1") != self.get_argument("userPass2"):
            alerts.append("Passwords do not match")
            logging.info("Failed to add new user; pwds don't match")
            self.render("signup.html", alerts = alerts)
        else:
            newEmail = self.get_argument("email1")
            salt = (bcrypt.gensalt()).decode("utf-8")
            password = (hashPwd(self.get_argument("userPass1"), salt)).decode("utf-8")
            uid = stringUUID()
            #returnValue = dbhandler.setUserInfo(newEmail, password, salt, uid)
            #if returnValue == True:
            #    self.set_secure_cookie("email", self.get_argument("email1"))
            #    logging.info("Added new user successfully")
            #else:
            #    logging.error("Failed to add a new user")
            #    logging.error(returnValue)
            #    self.render("signup.html", alerts = ["failed to sign you up",])

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html", message = "")

    def post(self):
        # Get the password info from the database
        info = dbhandler.getLoginEmail(self.get_argument("email"))
        if info != False:
            pwd = info['password']
            salt = info['salt']
            pwd = bytes(pwd, "ascii")
            userpass = self.get_argument("password")
            hasheduserpass = hashPwd(userpass, salt)
            if hasheduserpass == pwd:
                self.set_secure_cookie("email", self.get_argument("email"))
                self.redirect("/home")
            else:
                self.render("login.html", message = "The information you supplied did not match an existing account")
        else:
            self.render("login.html", message = "The information you supplied did not match an existing account")


def stringUUID():
    uid = uuid.uuid4()
    uid = uid.urn[9:]
    return(uid)

def hashPwd(pwd, salt):
    pwd = bytes(pwd, "ascii")
    salt = bytes(salt, "ascii")
    hashed = bcrypt.hashpw(pwd, salt)
    return(hashed)

enable_pretty_logging()
app = tornado.web.Application(
    [(r"/", RootHandler),(r"/signup", SignUpHandler), (r"/calculate", CalculateHandler),
    (r"/login", LoginHandler),],
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    )

http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(8080)

tornado.ioloop.IOLoop.instance().start()
