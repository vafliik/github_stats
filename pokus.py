import json
import os

import requests

TOKEN = os.environ['GITHUB_TOKEN']

r = requests.head('https://api.github.com/repos/salsita/circlesorg/pulls?state=closed&per_page=20', headers={'Authorization': 'token {}'.format(TOKEN)})

if 'next' in r.links.keys():
    print ('I has next')
    r2 = requests.head(r.links['last']['url'], headers={'Authorization': 'token {}'.format(TOKEN)} )

if 'last' in r.links.keys():
    print ('I has last')
    r2 = requests.head(r.links['last']['url'], headers={'Authorization': 'token {}'.format(TOKEN)} )

# jason = json.loads(r.text)

print(r.links)