import sqlite3, json, requests

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
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        name        TEXT                                  NOT NULL,
                        email       TEXT                                  NOT NULL,
                        departTime  DATE                                  NOT NULL,
                        timeBuffer  INTEGER                               NOT NULL,
                        stopTag     TEXT                                  NOT NULL,
                        busTag      TEXT                                  NOT NULL,
                        FOREIGN KEY(stopTag) REFERENCES StopsBusses(stopTag),
                        FOREIGN KEY(busTag) REFERENCES StopsBusses(busTag)
                        );''')

    except Error as e:
        print(e)
        conn.close()
        exit()

def populate(conn):
    routeResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=rutgers")
    routeResp.raise_for_status()
    busList = json.loads(routeResp.text)["route"]

    for b in busList[5:-7]:
        stopResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=rutgers&r=" + b["tag"])
        stopResp.raise_for_status()
        stopList = json.loads(stopResp.text)["route"]["stop"]

        #print("\nBus: %s | Tag: %s" % (b["title"], b["tag"]))
        for s in stopList:
            #print("\t%s | Tag: %s" % (s["title"], s["tag"]))
            conn.execute("INSERT INTO StopsBusses (stopTag, busTag, stopName, busName)" +
                            "VALUES (\'" + s["tag"] + "\', \'" + b["tag"] + "\', \'" + s["title"] + "\', \'" + b["title"] +"\');")

    conn.commit()

def main():
    conn = sqlite3.connect('databases\\busSniper.db')
    makeTables(conn)
    populate(conn)

    print("Success.")

if __name__ == "__main__":
    main()
