import json
import requests
import base64

from pathlib import Path

with open(Path(__file__).parent / 'credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

app_key = creds['key']
app_secret = creds['secret']
refresh_token = creds['refresh_token']

payload = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
}

headers = {
    'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{app_secret}", "utf-8")).decode("utf-8")}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.post(
    url="https://api.schwabapi.com/v1/oauth/token",
    headers=headers,
    data=payload,
)

if response.status_code == 200:
    print("Retrieved new tokens successfully using refresh token.")
else:
    print(f"Error refreshing access token: {response.text}")

response_dict = response.json()

creds['access_token'] = response_dict['access_token']
creds['refresh_token'] = response_dict['refresh_token']
creds['expires_in'] = response_dict['expires_in']

with open(Path(__file__).parent / 'credentials.json', 'w', encoding='utf-8') as f:
    json.dump(creds, f, indent=4)

print(response_dict)
