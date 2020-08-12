import requests
import urllib.parse
import re
import json
import os


fitbit_clientID=os.environ.get("FITBITOAUTH2CLIENTID")
redirect_url = os.environ.get("REDIRECT_URL")


def get_auth_url():
    encoded_url = urllib.parse.quote(redirect_url)
    auth_url = f"https://www.fitbit.com/oauth2/authorize?response_type=token&client_id={fitbit_clientID}&redirect_uri={encoded_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800"
    return auth_url

# user should follow auth_url, login to fitbit, and parse the url when it comes back to beetis dashboard


def get_user_access_token(resp_url):
    oauth_access_token = re.search("access_token=(.*)&user_id", resp_url).group(1)
    return oauth_access_token


def get_hr_today(oauth_access_token):
    headers = {"Authorization": f"Bearer {oauth_access_token}"}
    api_endpoint = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1sec/time/00:00/12:59.json"
    r = requests.get(url=api_endpoint, headers=headers)
    # data = json.loads(r.content)
    data = json.dumps(r.content.decode("utf-8"))
    return data
