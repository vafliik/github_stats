import json
import os

import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.environ['GITHUB_TOKEN']

def get_pulls(state=all, per_page=10):
    params = {'state': state, 'per_page': per_page}
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/pulls', params=params, headers={'Authorization': 'token {}'.format(TOKEN)})
    pull_requests = json.loads(r.text)
    return pull_requests

def get_events(pr_number):
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/issues/{}/events'.format(pr_number), headers={'Authorization': 'token {}'.format(TOKEN)})
    events = json.loads(r.text)
    return events

def duration(start_time, end_time):

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    return end_time - start_time
