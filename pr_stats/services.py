import json
import logging
import os

import dateutil.parser
import requests

from datetime import datetime, timezone, timedelta

from pr_stats.models import PullRequest, User

TOKEN = os.environ['GITHUB_TOKEN']

logger = logging.getLogger(__name__)


def get_users():
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/users',
                     headers={'Authorization': 'token {}'.format(TOKEN)})
    users = json.loads(r.text)
    return users


def get_pulls(state=all, per_page=10):
    params = {'state': state, 'per_page': per_page}
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/pulls', params=params,
                     headers={'Authorization': 'token {}'.format(TOKEN)})
    pull_requests = json.loads(r.text)
    return pull_requests


def get_events(pr_number):
    r = requests.get('https://api.github.com/repos/salsita/circlesorg/issues/{}/events'.format(pr_number),
                     headers={'Authorization': 'token {}'.format(TOKEN)})
    events = json.loads(r.text)
    return events


def get_all_pulls(state='all', per_page=30):

    params = {'state': state, 'per_page': per_page}

    response = github_reqest(url='https://api.github.com/repos/salsita/circlesorg/pulls', params=params)

    data = json.loads(response.text)
    prs_from_data(data)

    while 'next' in response.links.keys():
        response = github_reqest(url=response.links['next']['url'], params=params)
        data = json.loads(response.text)
        prs_from_data(data)

def update_pulls(last_updated):

    params = {'q': 'type:pr repo:salsita/circlesorg updated:>{}'.format(last_updated)}

    response = github_reqest(url='https://api.github.com/search/issues', params=params)

    data = json.loads(response.text)
    prs_from_data(data['items'])

    while 'next' in response.links.keys():
        response = github_reqest(url=response.links['next']['url'], params=params)
        data = json.loads(response.text)
        prs_from_data(data['items'])


def prs_from_data(data):

    for pull in data:
        save_pr_from_dict(pull)


def save_pr_from_dict(pull):

    user = create_user_if_not_already(pull['user'])

    pr, created = PullRequest.objects.update_or_create(
        pk = pull['number'],
        user = user,
        created_at = dateutil.parser.parse(pull['created_at']),
        html_url = pull['html_url']
    )

    pr.title = pull['title']
    pr.state = pull['state']
    pr.body = pull['body']
    pr.updated_at = dateutil.parser.parse(pull['updated_at'])
    if pull['closed_at'] is not None:
        pr.closed_at = dateutil.parser.parse(pull['closed_at'])
        pr.closed_after_sec = pr.time_open_sec()
    pr.save()

def create_user_if_not_already(user):
    user_created = User.objects.get_or_create(id=user['id'], login=user['login'], avatar_url=user['avatar_url'],
                                              url=user['url'])
    # tuple ({user}, created=True/False)
    return user_created[0]


def median_value(queryset, term):
    count = queryset.count()
    values = queryset.values_list(term, flat=True).order_by(term)
    if count % 2 == 1:
        return values[int(round(count / 2))]
    else:
        return sum(values[count / 2 - 1:count / 2 + 1]) / 2.0

def github_reqest(url, params=None):
    return requests.get(url=url, params=params,
                        headers={'Authorization': 'token {}'.format(TOKEN)})