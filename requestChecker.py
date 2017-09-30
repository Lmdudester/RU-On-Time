import sqlite3, json, requests, datetime, smtplib, time

class TimeKeeper():

    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

    #Adds a number of minutes to a TimeKeeper object
    def addMins(self, mins):
        if(self.minute + mins >= 60):
            while(mins >= 60):
                self.hour += 1
                mins -= 60
            if(self.minute + mins >= 60):
                self.hour += 1
                self.minute = self.minute + mins - 60
            else:
                self.minute = self.minute + mins
        elif(self.minute + mins < 0):
            while(mins <= -60):
                self.hour -= 1
                mins += 60
            if(self.minute + mins < 0):
                self.hour -= 1
                self.minute = self.minute + mins + 60
            else:
                self.minute = self.minute + mins
        else:
            self.minute = self.minute + mins

    #Returns the difference between two TimeKeepers in minutes
    #   positive if self >, negative if comp >, 0 otherwise
    def __cmp__(self, compTime):
        return self.minute - compTime.minute + (self.hour - compTime.hour)*60

    def __str__(self):
        return "%d:%02d" % (self.hour, self.minute)

#Send an email to the relevant user telling them to leave now
def sendEmail(conn, userId):
    cursor = conn.execute("SELECT name, email, busName, stopName FROM Requests JOIN StopsBusses ON (Requests.busTag = StopsBusses.busTag AND Requests.stopTag = StopsBusses.stopTag) WHERE id = " + str(userId) +";")
    usrInfo = cursor.fetchone()

    #Construct Email
    fromaddr = 'BusSniper'
    toaddrs  = usrInfo[1]
    msg = "\r\n".join(["From: MySniper", "To: " + usrInfo[1], usrInfo[0] + ",\n" + "Leave now to catch the " + usrInfo[2] + " at " + usrInfo[3] + "."])

    #Log in
    username = 'temp@website.com'
    password = 'ThePassword'
    server = smtplib.SMTP('smtp.gmail.com:587')

    #Send email
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

    print("Name: %s" % usrInfo[0])
    print("Email: %s" % usrInfo[1])
    print("BusName: %s" % usrInfo[2])
    print("StopName: %s" % usrInfo[3])

#Determines if an alert is required for the given request
def determineRequest(conn, currTime, request):
    predictions = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=predictions&a=rutgers&r=" + request[5] + "&s=" + request[4])
    predictions.raise_for_status()
    preList = json.loads(predictions.text)["predictions"]['direction']['prediction']

    #Creates a TimeKeeper object for the required leaving time
    reqTime = TimeKeeper(request[1], request[2])

    #Soonest prediciton is defaulted to best time
    bestTime = TimeKeeper(currTime.hour, currTime.minute)
    bestTime.addMins(int(preList[0]['minutes']))

    #While the current time plus the prediction is still before the required time
    #   keep trying to find the latest time
    for preDict in preList[1:]:
        tempTime = TimeKeeper(currTime.hour, currTime.minute)
        tempTime.addMins(int(preDict['minutes']))

        if(tempTime.__cmp__(reqTime) > 0):
            break
        else:
            bestTime = tempTime

    #Account for the walking time buffer
    bestTime.addMins(-1*request[3])

    #If its time to leave or the time to leave has passed alert the user
    if(currTime.__cmp__(bestTime) >= 0):
        bestTime.addMins(request[3])
        print("Leave now id: %d Catch: %s\n" % (request[0], str(bestTime)))

        #Send email
        sendEmail(conn, request[0])

        #Remove from table
        conn.execute("DELETE FROM Requests WHERE id = " + str(request[0]) + ";")
        conn.commit()

    #Otherwise, wait for next refresh
    else:
        bestTime.addMins(request[3])
        print("Request id: %d Best prediction: %s\n" % (request[0], str(bestTime)))

#Obtains and processes all relevant requests
def getRequests(conn):
    #Create a TimeKeeper object of the current time
    now = datetime.datetime.now()
    time = TimeKeeper(now.hour, now.minute)
    time.addMins(45)

    #Get every request within the threshold
    c = conn.execute("SELECT id, departHour, departMinute, timeBuffer, stopTag, busTag FROM Requests WHERE (departHour = " + str(time.hour) + " AND departMinute <= " + str(time.minute) + ") OR departHour < " + str(time.hour) + ";")

    #Bring time back to current time
    time.addMins(-45)
    print("Time: %s\n" % str(time))

    #Process each request
    for row in c:
        determineRequest(conn, time, row)

def main():
    #Connect to the database
    conn = sqlite3.connect('databases/busSniper.db')

    #Process requests every minute
    while(True):
        getRequests(conn)
        print("Success.")
        time.sleep(60)


    print("Success.")

if __name__ == "__main__":
    main()
