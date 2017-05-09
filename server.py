import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.log import enable_pretty_logging

import logging
import os.path
from datetime import datetime
import bcrypt

import dbhandler

# Class to define how to handle requests to the root of the website.
class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

# Class to define how the T&Cs page should be rendered.
class TermsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("terms.html")

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
        if info[0] != info[2]:
            alerts.append("Emails do not match")
            if info[2] != info[3]:
                alerts.append("Passwords do not match")
                logging.info("Failed to add new user; neither match")
                self.render("signup.html", alerts = alerts)
            else:
                self.render("signup.html", alerts = alerts)
                logging.info("Failed to add new user; emails don't match")
        elif info[2] != info[3]:
            alerts.append("Passwords do not match")
            logging.info("Failed to add new user; pwds don't match")
            self.render("signup.html", alerts = alerts)
        else:
            newEmail = info[0]
            if dbhandler.checkEmail(newEmail) == True:
                salt = (bcrypt.gensalt()).decode("utf-8")
                password = (hashPwd(info[2], salt)).decode("utf-8")
                returnValue = dbhandler.setUserInfo(newEmail, password, salt)
                if returnValue == True:
                    self.set_secure_cookie("email", info[0])
                    logging.info("Added new user successfully")
                    self.redirect("/home")
                else:
                    logging.error("Failed to add a new user")
                    logging.error(returnValue)
                    self.render("signup.html", alerts = ["Sign Up failed.",])
            else:
                alerts.append("Email address already in use, please try again.")
                self.render("signup.html", alerts = alerts)

# Class to define how the login page and requests should be handled. Including
# matching input data to that of the database.
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("email"):
            self.render("login.html", message = "")
        else:
            self.redirect("/home")

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

# Class to define how a user should be logged out of the service.
class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_secure_cookie("email"):
            self.clear_cookie("email")
            self.redirect("/")
        else:
            self.redirect("/")

# Class to define how requests to the "/home" URL are handled.
class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("email"):
            self.redirect("/signup")
        else:
            email = self.get_secure_cookie("email").decode("utf-8")
            userID = dbhandler.getUserID(email)['ID']
            shifts = dbhandler.getShifts(userID)
            formatedShifts = []
            for shift in shifts:
                formatedShifts.append(
                {
                "startDate" : shift['startTime'].strftime("%m/%d/%Y"),
                "startTime" : shift['startTime'].strftime("%H:%M"),
                "endTime" : shift['endTime'].strftime("%H:%M"),
                "ID" : shift['ID']
                }
                )
            self.render("home.html", shifts = formatedShifts)

# Class to define how requests to the "/newShift" URL are handled. Includes
# addind a new shift to the database, does not calculate pay.
class NewShiftHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("email"):
            self.redirect("/login")
        else:
            self.render("newShifts.html")

    def post(self):
        email = self.get_secure_cookie("email").decode("utf-8")
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
            self.redirect("/newShift")
        breakLength = float(self.get_argument("breakLength"))
        wage = float(self.get_argument("hourlyWage"))
        userID = dbhandler.getUserID(email)['ID']
        returnValue = dbhandler.addNewShift(startDateTime, endDateTime, breakLength, wage, userID)
        if returnValue != True:
            logging.error(returnValue)
            self.render("newShifts.html")
        else:
            self.redirect("/home")

# Class to define how users should be able to edit shifts that they have already
# saved to the database. Also gives more detailed info about shift.
class EditShiftHandler(tornado.web.RequestHandler):
    def get(self, url):
        # Validate user exists.
        email = self.get_secure_cookie("email").decode("utf-8")
        userID = dbhandler.getUserID(email)
        if userID != None:
            userID = userID['ID']
        else:
            self.redirect("/home")
        # Validate that the shift being edited belongs to that user.
        shiftID = url.rsplit("/", 1)
        shiftID = (shiftID[(len(shiftID) - 1)])
        shiftUserID = dbhandler.getShiftUserID(shiftID)
        if shiftUserID != None:
            shiftUserID = shiftUserID['userID']
        else:
            self.redirect("/home")
        # Get shift info to be rendered to document.
        shift = dbhandler.getShiftInfo(shiftID)
        shiftInfo = {
        'date' : shift['startTime'].strftime("%d/%m/%Y"),
        'startTime' : shift['startTime'].strftime("%H:%M"),
        'endTime' : shift['endTime'].strftime("%H:%M"),
        'breakLength' : shift['break_length'],
        'pay' : calculatePay(shift['startTime'], shift['endTime'], shift['break_length'], shift['pay'])
        }
        if shiftUserID == userID:
            self.render("editShift.html", info = shiftInfo)
        else:
            self.redirect("/home")

    def post(self, url):
        # Validate user exists.
        email = self.get_secure_cookie("email").decode("utf-8")
        userID = dbhandler.getUserID(email)
        if userID != None:
            userID = userID['ID']
        else:
            self.redirect("/home")
        # Validate that the shift being edited belongs to that user.
        shiftID = url.rsplit("/", 1)
        shiftID = (shiftID[(len(shiftID) - 1)])
        shiftUserID = dbhandler.getShiftUserID(shiftID)
        if shiftUserID != None:
            shiftUserID = shiftUserID['userID']
        else:
            self.redirect("/home")
        # Get change info from form.
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
            self.redirect("/newShift")
        breakLength = float(self.get_argument("breakLength"))
        wage = float(self.get_argument("hourlyWage"))
        # Attempt to commit changes to database.
        returnValue = dbhandler.editShiftInfo(shiftID, startDateTime, endDateTime, breakLength, wage)
        if returnValue != True:
            logging.error(returnValue)
            self.redirect("/editShift/{0}".format(shiftID))
        else:
            self.redirect("/editShift/{0}".format(shiftID))

# Class to define how payday information should be displayed.
class PayDayHandler(tornado.web.RequestHandler):
    def get(self, url):
        email = self.get_secure_cookie("email").decode("utf-8")
        userID = dbhandler.getUserID(email)['ID']
        shifts = dbhandler.getShifts(userID)
        shiftInfo = []
        payInfo = {
        'date' : "TEST 04/04/2017",
        'pay' : 500
        }
        for shift in shifts:
            shiftInfo.append(
            {
            "startDate" : shift['startTime'].strftime("%m/%d/%Y"),
            "startTime" : shift['startTime'].strftime("%H:%M"),
            "endTime" : shift['endTime'].strftime("%H:%M"),
            "ID" : shift['ID']
            }
            )
        self.render("payday.html", shifts = shiftInfo, payInfo = payInfo)

# Function to decode and hash a given plaintext password and a salt.
def hashPwd(pwd, salt):
    pwd = bytes(pwd, "ascii")
    salt = bytes(salt, "ascii")
    hashed = bcrypt.hashpw(pwd, salt)
    return(hashed)

# Function to calculate the amount a shift pays based on wage, length, and break length.
def calculatePay(startTime, endTime, breakLength, wage):
    timeDelta = endTime - startTime
    tdDecimal = (timeDelta.seconds / 3600)
    tdDecimal = tdDecimal - float(breakLength)
    return(tdDecimal * float(wage))

enable_pretty_logging()
app = tornado.web.Application(
    [(r"/", RootHandler),(r"/signup", SignUpHandler), (r"/calculate", CalculateHandler),
    (r"/login", LoginHandler), (r"/home", HomeHandler), (r"/newShift", NewShiftHandler),
    (r"/logout", LogoutHandler), (r"/editShift/(.*)", EditShiftHandler),
    (r"/terms", TermsHandler), (r"/payday/(.*)", PayDayHandler),],
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret = "secret",
    debug = True,
    )

http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(8080)

tornado.ioloop.IOLoop.instance().start()
