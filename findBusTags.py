import json, requests

#Request Agency Listing
agencyResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=agencyList")
agencyResp.raise_for_status()
agencyList = json.loads(agencyResp.text)

#Obtain tag for Rutgers
for i in agencyList["agency"]:
    if "Rutgers University" == i["title"]:
        rutgersDict = i

#Get Route List
routeResp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=" + rutgersDict["tag"])
routeResp.raise_for_status()
busDict = json.loads(routeResp.text)

#busDict now has all bus routes and their tags inside
