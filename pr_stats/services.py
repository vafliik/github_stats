import json
import os

import requests

TOKEN = os.environ['GITHUB_TOKEN']

def get_pulls():
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/pulls?state=all&per_page=20', headers={'Authorization': 'token {}'.format(TOKEN)})
    pull_requests = json.loads(r.text)
    return pull_requests

def get_events(pr_number):
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/issues/{}/events'.format(pr_number), headers={'Authorization': 'token {}'.format(TOKEN)})
    events = json.loads(r.text)
    return events