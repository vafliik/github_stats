import requests
import json

from datetime import datetime, timezone, timedelta
import dateutil.parser

TOKEN = '97fe76db190e3e7be8d517466405e3f6241b9b2f'

def duration(start_time, end_time):
    start_time = dateutil.parser.parse(start_time)

    if end_time is None:
       end_time = datetime.now(timezone.utc)
    else:
       end_time = dateutil.parser.parse(end_time)

    return end_time - start_time


number_pr = 0
total_pr_time = timedelta(0)
fastest_pr = 0, None, timedelta.max
slowest_pr = 0, None, timedelta(0)
labels_duration = {}
labels_pr_added = {}
labels_pr_removed = {}

#maybe straight to /issues ? We do not use them for anything else than PRs
r = requests.get('https://api.github.com/repos/salsita/circlesorg/pulls?state=all&per_page=100', headers={'Authorization': 'token {}'.format(TOKEN)})

if(r.ok):
    repoItem = json.loads(r.text)
    for pr in repoItem:
        number_pr += 1

        print('{:-^50}'.format('Pull Request ' + str(pr['number'])))
        print(pr['title'])
        pr_duration = duration(pr['created_at'], pr['closed_at'])

        if pr_duration > slowest_pr[2]:
            slowest_pr = pr['number'], pr['title'], pr_duration
        if pr_duration < fastest_pr[2] and pr['state'] != 'open':
            fastest_pr = pr['number'], pr['title'], pr_duration


        total_pr_time += pr_duration
        print("Open for {}".format(pr_duration))

        event_r = requests.get(pr['issue_url'] + '/events', headers={'Authorization': 'token {}'.format(TOKEN)})

        events = json.loads(event_r.text)

        for event in events:
            if event['event'] == 'unlabeled':

                event_duration = duration(pr['created_at'], event['created_at'])
                label_name = event['label']['name']

                if label_name in labels_duration:
                    labels_duration[label_name] += event_duration
                    labels_pr_removed[label_name] += 1
                else:
                    labels_duration[label_name] = event_duration
                    labels_pr_removed[label_name] = 1

                print('Label [ {} ] removed after {}'.format(label_name, event_duration))

            elif event['event'] == 'labeled':

                label_name = event['label']['name']

                if label_name in labels_pr_added:
                    labels_pr_added[label_name] += 1
                else:
                    labels_pr_added[label_name] = 1


print('{:*^60}'.format('Stats'))
print('Average time of PR open: {}\n'.format(total_pr_time / number_pr))
print('Slowest PR: {}, {} (Took: {})'.format(slowest_pr[0], slowest_pr[1], slowest_pr[2]))
print('Fastest PR: {}, {} (Took: {})'.format(fastest_pr[0], fastest_pr[1], fastest_pr[2]))

print('{:.^60}'.format('Labels usage'))
for label in labels_duration.keys():
    print("[ {} ]".format(label))
    print("Added to {} pull requests.".format(labels_pr_added[label]))
    print("Removed from {} pull requests.".format(labels_pr_removed[label]))
    print('Average time until removed: {}'.format(labels_duration[label] / labels_pr_removed[label]))




