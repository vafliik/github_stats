import json
import logging
import os

import dateutil.parser
import requests

from pr_stats.models import PullRequest, User, Event

TOKEN = os.environ['GITHUB_TOKEN']

logger = logging.getLogger("service")


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


def update_pulls(last_updated=None, q=None):

    if q is None:
        if last_updated is not None:
            logger.info("Last updated: " + last_updated)
            params = {'q': 'type:pr repo:salsita/circlesorg updated:>{}'.format(last_updated)}
        else:
            params = {'q': 'type:pr repo:salsita/circlesorg'}

        response = github_reqest(url='https://api.github.com/search/issues', params=params)

    else:
        response = github_reqest(url='https://api.github.com/search/issues?q=type:pr+repo:salsita/circlesorg+created:' + q)

    data = json.loads(response.text)
    logger.warn(data)
    prs_from_data(data['items'])

    while 'next' in response.links.keys():
        response = github_reqest(url=response.links['next']['url'])
        data = json.loads(response.text)
        prs_from_data(data['items'])


def prs_from_data(data):
    for pull in data:
        logger.info("Processing PR: {} {}, created: {}".format(pull['number'], pull['title'], pull['created_at']))
        pr = save_pr_from_dict(pull)
        add_events_to_pr(pr)


def save_pr_from_dict(pull):
    user = create_user_if_not_already(pull['user'])

    pr, created = PullRequest.objects.update_or_create(
        pk=pull['number'],
        user=user,
    )

    pr.created_at = dateutil.parser.parse(pull['created_at'])
    pr.html_url = pull['html_url']
    pr.title = pull['title']
    pr.state = pull['state']
    pr.body = pull['body']
    pr.updated_at = dateutil.parser.parse(pull['updated_at'])
    if pull['closed_at'] is not None:
        pr.closed_at = dateutil.parser.parse(pull['closed_at'])
        pr.closed_after_sec = pr.time_open_sec()
    pr.save()

    return pr


def add_events_to_pr(pr):
    logger.info("Getting events fo PR {}".format(pr.pk))
    events = get_events(pr.pk)

    for event in events:
        e, created = Event.objects.get_or_create(
            pull_request=pr,
            id=event['id'],
            event=event['event'],
            label=event['label']['name'] if 'label' in event.keys() else None,
            actor=create_user_if_not_already(event['actor']),
            created_at=dateutil.parser.parse(event['created_at']),
        )

        if created:
            logger.info("- Created event {}: {}".format(e.id, e.event))


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
