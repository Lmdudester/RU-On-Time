import json, requests

#Returns a list of dictionaries where each dictionary contains a bus route's tag and title
def getBusRteDict():
    #Request Agency Listing
    agencyResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=agencyList")
    agencyResp.raise_for_status()
    agencyList = json.loads(agencyResp.text)

    #Obtain tag for Rutgers
    for i in agencyList["agency"]:
        if "Rutgers University" == i["title"]:
                #Get Route List
                routeResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=" + i["tag"])
                routeResp.raise_for_status()
                busDict = json.loads(routeResp.text)

                #Returned value has a list of all bus routes and their tags inside
                return busDict["route"]

    print("Rutgers University Agency Not Found...")

for i in getBusRteDict():
    print(i)
