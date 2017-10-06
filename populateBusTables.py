import sqlite3, json, requests, datetime

# **makeTables()**
# Drop old tables and create the new ones
# Args:
#   conn - the connection to the database
# Return:
#   N/A
def makeTables(conn):
    try:
        conn.execute('''DROP TABLE IF EXISTS StopsBusses''')
        conn.execute('''DROP TABLE IF EXISTS Requests''')

        conn.execute('''CREATE TABLE StopsBusses (
                        stopTag     TEXT                                  NOT NULL,
                        busTag      TEXT                                  NOT NULL,
                        stopName    TEXT                                  NOT NULL,
                        busName     TEXT                                  NOT NULL,
                        PRIMARY KEY (stopTag, busTag)
                        );''')

        conn.execute('''CREATE TABLE Requests (
                        id           INTEGER PRIMARY KEY AUTOINCREMENT,
                        name         TEXT                                  NOT NULL,
                        email        TEXT                                  NOT NULL,
                        departHour   INTEGER                               NOT NULL,
                        departMinute INTEGER                               NOT NULL,
                        timeBuffer   INTEGER                               NOT NULL,
                        stopTag      TEXT                                  NOT NULL,
                        busTag       TEXT                                  NOT NULL,
                        FOREIGN KEY(stopTag) REFERENCES StopsBusses(stopTag),
                        FOREIGN KEY(busTag) REFERENCES StopsBusses(busTag)
                        );''')

    except Error as e:
        print(e)
        conn.close()
        exit()

# **populate()**
# Populate the StopsBusses table with the relevant bus data for the day
# Args:
#   conn - the connection to the database
# Return:
#   N/A
def populate(conn):
    routeResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=rutgers")
    routeResp.raise_for_status()
    busList = json.loads(routeResp.text)["route"]

    if(datetime.datetime.today().weekday() < 5):
        busList = busList[5:-7]
    else:
        busList = busList[-4:-2]

    for b in busList:
        stopResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=rutgers&r=" + b["tag"])
        stopResp.raise_for_status()
        stopList = json.loads(stopResp.text)["route"]["stop"]

        for s in stopList:
            conn.execute("INSERT INTO StopsBusses (stopTag, busTag, stopName, busName)" +
                            "VALUES (\'" + s["tag"] + "\', \'" + b["tag"] + "\', \'" + s["title"] + "\', \'" + b["title"] +"\');")

    conn.commit()

def main():
    #Connect to or create the database file
    conn = sqlite3.connect('databases/busSniper.db')

    #Drop old tables and create new ones
    makeTables(conn)

    #Populate the StopsBusses table with the relevant bus data
    populate(conn)

    print("Success.")

if __name__ == "__main__":
    main()
