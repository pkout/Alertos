import json
import requests

from pathlib import Path

base_url = "https://api.schwabapi.com/trader/v1"

with open(Path(__file__).parent / 'credentials.json', encoding='utf-8') as f:
    creds = json.load(f)

response = requests.get(
    f'{base_url}/accounts/accountNumbers',
    headers={'Authorization': f'Bearer {creds["access_token"]}'}
)

print(response.json())