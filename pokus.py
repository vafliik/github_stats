import json
import os
import requests

TOKEN = os.environ['GITHUB_TOKEN']

params = {'q': 'type:pr author:vafliik repo:salsita/circlesorg updated:>2016-09-06T20:29:09+00:00'}

r = requests.get('https://api.github.com/search/issues', params=params,
                 headers={'Authorization': 'token {}'.format(TOKEN)})

data = json.loads(r.text)

for pr in data['items']:
    print(pr['title'], pr['updated_at'])
