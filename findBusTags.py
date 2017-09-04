import json, requests

class NBBusses:
    agency = ""
    busList = []

    #Request the agency string, then obtain the bus list
    def __init__(self):
        #Request Agency Listing
        agencyResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=agencyList")
        agencyResp.raise_for_status()
        agencyList = json.loads(agencyResp.text)

        #Obtain tag for Rutgers
        for i in agencyList["agency"]:
            if "Rutgers University" == i["title"]:
                    self.agency = i["tag"]

                    #Get Route List
                    routeResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=" + i["tag"])
                    routeResp.raise_for_status()
                    self.busList = json.loads(routeResp.text)["route"]
                    return

        print("Rutgers University Agency Not Found...")

    #Given a route's Tag, return the list of stops
    def getStopList(self, routeTag):
        stopResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=" + self.agency + "&r=" + routeTag)
        stopResp.raise_for_status()
        stopList = json.loads(stopResp.text)

        return stopList["route"]["stop"]

tempBusses = NBBusses()

#Print bus Routes
for i in tempBusses.busList:
    print(i)

#Print stops for the "A" bus
for i in tempBusses.getStopList(tempBusses.busList[5]["tag"]):
    print(i)
