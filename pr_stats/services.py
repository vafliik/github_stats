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


def save_pulls(state='all', per_page=30):

    params = {'state': state, 'per_page': per_page}

    response = github_reqest(url='https://api.github.com/repos/salsita/circlesorg/pulls', params=params)

    try:
        prs_from_response(response)

        while 'next' in response.links.keys():
            response = github_reqest(url=response.links['next']['url'], params=params)
            prs_from_response(response)

    except Pull_Request_Exists:
        return


def prs_from_response(response):
    pull_requests = json.loads(response.text)
    for pull in pull_requests:
        save_pr_from_dict(pull)


def save_pr_from_dict(pull):

    try:
        PullRequest.objects.get(pk=pull['number'])
        raise Pull_Request_Exists

    except PullRequest.DoesNotExist:
        pr = PullRequest()
        pr.number = pull['number']
        pr.title = pull['title']
        pr.user = create_user_if_not_already(pull['user'])
        pr.state = pull['state']
        pr.body = pull['body']
        pr.created_at = dateutil.parser.parse(pull['created_at'])
        pr.updated_at = dateutil.parser.parse(pull['updated_at'])
        if pull['closed_at'] is not None:
            pr.closed_at = dateutil.parser.parse(pull['closed_at'])
            pr.closed_after_sec = pr.time_open_sec()
        pr.html_url = pull['html_url']
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

class Pull_Request_Exists(Exception):
    pass
