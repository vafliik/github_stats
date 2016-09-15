import json
import os
import requests

TOKEN = os.environ['GITHUB_TOKEN']

params = {'q': 'type:pr author:vafliik repo:salsita/circlesorg updated:2016-08-09..2016-08-15'}

r = requests.get('https://api.github.com/search/issues', params=params,
                 headers={'Authorization': 'token {}'.format(TOKEN)})

data = json.loads(r.text)

for pr in data['items']:
    print(pr['title'], pr['updated_at'])
