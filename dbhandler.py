import pymysql
import yaml
import uuid

# Function to make connection to the database. Reads the parameters out of a
# configuration file. Returns the connection object for use by other functions.
def makeConnection():
    with open("dbconfig.yaml", 'r') as stream:
        try:
            config = yaml.load(stream)
            connection = pymysql.connect(host = config['MySQL']['hostname'],
                                        user = config['MySQL']['user'],
                                        password = config['MySQL']['password'],
                                        db = config['MySQL']['database'],
                                        charset = "utf8mb4",
                                        cursorclass = pymysql.cursors.DictCursor)
            return(connection)
        except Exception as e:
            return("Error: {0}".format(e))

# Function to set user information
def setUserInfo(email, password, salt):
    connection = makeConnection()
    try:
        # Initialise the cursor, which is used to perform tasks on the DB
        with connection.cursor() as cursor:
            # Insert new record, ID is blank as is self incrementing
            sql = ("INSERT INTO users (email, password, salt) VALUES ('{0}', '{1}', '{2}')")
            cursor.execute(sql.format(email, password, salt,))
        # Commit the changes made to the DB
        connection.commit()
        return(True)
    # Handle any errors on MySQL's part
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

# Function to check if the new sign-up's email is already in use, returns False
# if not in use
def checkEmail(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT email FROM users WHERE email = '{0}'")
            returnVal = cursor.execute(sql.format(email))
            if returnVal == 0:
                return(True)
            else:
                return(False)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

# Function to get the login information of a given account
def getLoginEmail(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT password, salt FROM users WHERE email = '{0}'")
            returnValue = cursor.execute(sql.format(email))
            if returnValue == 0:
                return(False)
            else:
                return(cursor.fetchone())
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

# Function to add a new shift to the database.
def addNewShift(startDateTime, endDateTime, breakLength, pay, userID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("INSERT INTO shifts (startTime, endTime, break_length, pay, userID) VALUES ('{0}', '{1}', {2}, {3}, '{4}')")
            cursor.execute(sql.format(startDateTime, endDateTime, breakLength, pay, userID))
        connection.commit()
        return(True)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

def getShifts(userID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT ID, startTime, endTime FROM shifts WHERE userID = '{0}' ORDER BY startTime DESC")
            cursor.execute(sql.format(userID))
            shifts = cursor.fetchall()
            return(shifts)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

def getUserID(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT ID FROM users WHERE email = '{0}'")
            cursor.execute(sql.format(email))
            ID = cursor.fetchone()
            return(ID)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

def getShiftUserID(shiftID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT userID from shifts WHERE ID = {0}")
            cursor.execute(sql.format(shiftID))
            userID = cursor.fetchone()
            return(userID)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

def getShiftInfo(shiftID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT startTime, endTime, pay, break_length FROM shifts WHERE ID = {0}")
            cursor.execute(sql.format(shiftID))
            return(cursor.fetchone())
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()

def editShiftInfo(shiftID, startTime, endTime, breakLength, pay):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("UPDATE shifts SET startTime = '{0}', endTime = '{1}', break_length = {2}, pay = {3} WHERE ID = '{4}'")
            cursor.execute(sql.format(startTime, endTime, breakLength, pay, shiftID))
        connection.commit()
        return(True)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e.args[1], e.args[0]))
    finally:
        connection.close()
