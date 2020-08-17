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


def get_user_access_token(resp_url):
    oauth_access_token = re.search("access_token=(.*)&user_id", resp_url).group(1)
    return oauth_access_token

