import json
import os

import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.environ['GITHUB_TOKEN']

def get_users():
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/users', headers={'Authorization': 'token {}'.format(TOKEN)})
    users = json.loads(r.text)
    return users

def get_pulls(state=all, per_page=10):
    params = {'state': state, 'per_page': per_page}
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/pulls', params=params, headers={'Authorization': 'token {}'.format(TOKEN)})
    pull_requests = json.loads(r.text)
    return pull_requests

def get_events(pr_number):
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/issues/{}/events'.format(pr_number), headers={'Authorization': 'token {}'.format(TOKEN)})
    events = json.loads(r.text)
    return events

def median_value(queryset, term):
    count = queryset.count()
    values = queryset.values_list(term, flat=True).order_by(term)
    if count % 2 == 1:
        return values[int(round(count/2))]
    else:
        return sum(values[count/2-1:count/2+1])/2.0