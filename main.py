import requests
import json

from datetime import datetime, timezone, timedelta
import dateutil.parser

TOKEN = ''

def duration(start_time, end_time):
    start_time = dateutil.parser.parse(start_time)

    if end_time is None:
       end_time = datetime.now(timezone.utc)
    else:
       end_time = dateutil.parser.parse(end_time)

    return end_time - start_time


number_pr = 0
total_pr_time = timedelta(0)
labels_duration = {}
labels_pr_count = {}

#maybe straight to /issues ? We do not use them for anything else than PRs
r = requests.get('https://api.github.com/repos/salsita/circlesorg/pulls?state=open&per_page=100', headers={'Authorization': 'token {}'.format(TOKEN)})

if(r.ok):
    repoItem = json.loads(r.text)
    for pr in repoItem:
        number_pr += 1

        print('{:-^50}'.format('Pull Request ' + str(pr['number'])))
        print(pr['title'])
        pr_duration = duration(pr['created_at'], pr['closed_at'])
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
                    labels_pr_count[label_name] += 1
                else:
                    labels_duration[label_name] = event_duration
                    labels_pr_count[label_name] = 1

                print('Label [ {} ] removed after {}'.format(label_name, event_duration))


print('{:*^60}'.format('Stats'))
print('Average time of PR open: {}'.format(total_pr_time / number_pr))
for label in labels_duration.keys():
    print('Average time until [{}] removed: {}'.format(label, labels_duration[label] / labels_pr_count[label]))




