import json
import requests

def fitbit_heart(oauth_access_token):
    headers = {"Authorization": f"Bearer {oauth_access_token}"}
    api_endpoint = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1sec/time/00:00/23:59.json"
    r = requests.get(url=api_endpoint, headers=headers)
    j = json.loads(r.content)
    return j
    # print(j)
    # activities_heart = pd.DataFrame(j["activities-heart"][0]["heartRateZones"])
    # heart_intraday = pd.DataFrame(j["activities-heart-intraday"]["dataset"])
    # return activities_heart, heart_intraday

