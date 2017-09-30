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

#Obtains and processes all relevant requests
def getRequests(conn, currTime, timeBuffer):
    currTime.addMins(timeBuffer)

    #Get every request within the threshold
    c = conn.execute("SELECT id, departHour, departMinute, timeBuffer, stopTag, busTag FROM Requests WHERE (departHour = " + str(currTime.hour) + " AND departMinute <= " + str(currTime.minute) + ") OR departHour < " + str(currTime.hour) + ";")

    #Bring time back to current time
    currTime.addMins(-1*timeBuffer)

    return c

def createGreedyDict(conn, currTime):
    preDict = {}
    busTags = conn.execute("SELECT busTag FROM StopsBusses GROUP BY busTag")

    for btag in busTags:
        preDict[btag[0]] = {}

        stopTags = conn.execute("SELECT stopTag FROM StopsBusses WHERE busTag = \'" + btag[0] + "\' GROUP BY stopTag;")

        for stag in stopTags:
            preDict[btag[0]][stag[0]] = []

            predictions = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=predictions&a=rutgers&r=" + btag[0] + "&s=" + stag[0])
            predictions.raise_for_status()
            preList = json.loads(predictions.text)["predictions"]['direction']['prediction']

            for timeDict in preList:
                temp = TimeKeeper(currTime.hour, currTime.minute)
                temp.addMins(int(timeDict['minutes']))
                preDict[btag[0]][stag[0]] += [ temp ]

    return preDict

#Determines if an alert is required for the given request
def processRequest(conn, preDict, currTime, request):
    reqPreList = preDict[request[5]][request[4]]

    #Creates a TimeKeeper object for the required leaving time
    reqTime = TimeKeeper(request[1], request[2])

    #Soonest prediciton is defaulted to best time
    suggTime = reqPreList[0]

    #While the current time plus the prediction is still before the required time
    #   keep trying to find the latest time
    for preDict in reqPreList[1:]:
        if(preDict.__cmp__(reqTime) > 0):
            break
        else:
            suggTime = preDict

    arriveTime = TimeKeeper(suggTime.hour, suggTime.minute)

    #Account for the walking time buffer
    arriveTime.addMins(-1*request[3])

    #If its time to leave or the time to leave has passed alert the user
    if(currTime.__cmp__(arriveTime) >= 0):
        arriveTime.addMins(request[3])
        print("Leave Now\tID: %d - Catch: %s\n" % (request[0], str(arriveTime)))

        #Send email
        sendEmail(conn, request[0])

        #Remove from table
        conn.execute("DELETE FROM Requests WHERE id = " + str(request[0]) + ";")
        conn.commit()

    #Otherwise, wait for next refresh
    else:
        arriveTime.addMins(request[3])
        print("Request ID: %d - Best prediction: %s\n" % (request[0], str(arriveTime)))

def main():
    #Connect to the database
    conn = sqlite3.connect('databases/busSniper.db')

    #Process requests every minute
    while(True):
        #Create a TimeKeeper object of the current time
        now = datetime.datetime.now()
        currTime = TimeKeeper(now.hour, now.minute)
        print("Log Time: %s\n" % str(currTime))

        requests = getRequests(conn, currTime, 45)

        preDict = createGreedyDict(conn, currTime)

        for request in requests:
           processRequest(conn, preDict, currTime, request)

        print("Success.")
        time.sleep(60)

    print("Success.")

if __name__ == "__main__":
    main()
