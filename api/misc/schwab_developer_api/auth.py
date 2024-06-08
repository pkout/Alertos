import json
import requests
import base64

from pathlib import Path

with open(Path(__file__).parent / 'credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

app_key = creds['key']
app_secret = creds['secret']

authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1'

print(f"Click to authenticate: {authUrl}")

returnedLink = input("Paste the redirect URL here: ")

code = f"{returnedLink[returnedLink.index('code=')+5:returnedLink.index('%40')]}@"

headers = {
    'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{app_secret}", "utf-8")).decode("utf-8")}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': 'authorization_code',
    'code': code, 'redirect_uri': 'https://127.0.0.1'
}

response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
response_dict = response.json()

access_token = response_dict['access_token']
refresh_token = response_dict['refresh_token']
expires_in = response_dict['expires_in']

base_url = "https://api.schwabapi.com/trader/v1/"

response = requests.get(
    f'{base_url}/accounts/accountNumbers',
    headers={'Authorization': f'Bearer {access_token}'}
)

creds['access_token'] = access_token
creds['refresh_token'] = refresh_token
creds['expires_in'] = expires_in

with open(Path(__file__).parent / 'credentials.json', 'w', encoding='utf-8') as f:
    json.dump(creds, f, indent=4)

print('Response:', response_dict)
print('Access token:', access_token)
print('Refresh token:', refresh_token)
