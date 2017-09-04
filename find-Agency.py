import json, requests

resp = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=agencyList")

busDict = json.loads(resp.text)

temp = 0

for i in busDict["agency"]:
    if "Rutgers" in i["title"]:
        print (str(temp) + ": " + i["title"])
    temp += 1
