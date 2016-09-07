# GitHub PR stats
Simple Pull Request statistics

It is not done yet. And so far it does not work much :)

# # main.py
Simple python script - can be run simply by `python3 main.py`

The path to repo is hardcoded, needs to be modified in the script
The query to fetch the PRs can be modified, see [API reference](https://developer.github.com/v3/pulls/#list-pull-requests)

Also, environmental variable `GITHUB_TOKEN` with GitHub token needs to be set

# # django web application

**Steps to run the app locally**

1. `python3 manage.py makemigrations` - create the migration file based on models in the app

2. `python3 manage.py migrate` - apply the migrations

3. `python3 manage.py runserver` - start the webserwer, by default on localhost:8000

# # Python requirements

`pip install Django`

`pip install python-dateutil`

# # # TODO

* Async loading (now only wait and redirect)
* Get labels with PRs (now the labels are downloaded only if PR detail is displayed, plus it does not update)
* Repo management - get rid of the hardcoded values

