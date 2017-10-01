import sqlite3

# **getInput()**
# Loops question to get a valid response
# Args:
#   reqStr - the question or prompt for the user
#   failStr - what to print if the input is invalid
#   choiceList - a list of valid strings the user can type
# Return:
#   The valid response string the user typed
def getInput(reqStr, failStr, choiceList):
    resp = input(reqStr).lower()

    while(not (resp in choiceList)):
        print(failStr)

        resp = input(reqStr)

    return resp

def main():
    #Connect to or create the database file
    conn = sqlite3.connect('databases/busSniper.db')

    #Start looping
    resp = 'n'
    while resp == 'n':
        #Get Request Info
        name = input("Name: ")
        print()
        email = input("Email: ")
        print()
        hour = int(getInput("Depart Hour: (0-24) ", "Not a valid hour.\n", [str(x) for x in range(0, 23)]))
        print()
        minute = int(getInput("Depart Minute: (0-59) ", "Not a valid minute.\n", [str(x) for x in range(0, 59)]))
        print()
        timeBuff = int(getInput("Depart Buffer: (0-15) ", "Not a valid depart buffer.\n", [str(x) for x in range(0, 15)]))

        #Pull bus names and only allow valid bus names
        busInfo = conn.execute("SELECT busName, busTag FROM StopsBusses GROUP BY busTag;")
        busTagList = []

        for bus in busInfo:
            print("Bus Name: %s..........Tag: %s" % (bus[0], bus[1]))
            busTagList += [ bus[1] ]

        print()
        bus = getInput("Bus Tag: ", "Not a valid bus tag.\n", busTagList)

        #Pull stop names for the selected bus and only allow valid stop names
        stopInfo = conn.execute("SELECT stopName, stopTag FROM StopsBusses WHERE busTag = \'" + bus + "\' GROUP BY stopTag;")
        stopTagList = []

        for stop in stopInfo:
            print("Stop Name: %s..........Tag: %s" % (stop[0], stop[1]))
            stopTagList += [ stop[1] ]

        print()
        stop = getInput("Stop Tag: ", "Not a valid stop tag.\n", stopTagList)

        #Give the user a chance to review the data they want to enter
        print("\n----Review Info----")
        print("Name: %s" % name)
        print("Email: %s" % email)
        print("Time: %d:%02d" % (hour, minute))
        print("Buffer: %d" % timeBuff)
        print("Bus: %s" % bus)
        print("Stop: %s\n" % stop)

        resp = getInput("Is this info correct? (Y/N)", "Not a valid response.", ['y', 'n'])

    #Enter the data into the database
    conn.execute("INSERT INTO Requests (name, email, departHour, departMinute, timeBuffer, busTag, stopTag) VALUES (\'" +
                    name + "\', \'" + email + "\', " + str(hour) + ", " + str(minute) + ", " + str(timeBuff) + ", \'" + bus + "\', \'" +
                    stop + "\');")
    conn.commit()

if __name__ == "__main__":
    main()
