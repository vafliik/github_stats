from datetime import datetime, timezone, timedelta
import time

from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=30)
    avatar_url = models.URLField(null=True)
    url = models.URLField(null=True)

    def __str__(self):
        return self.login


class PullRequest(models.Model):
    number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=30)
    body = models.TextField(default='')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    closed_after_sec = models.IntegerField(blank=True, null=True)
    html_url = models.URLField(null=True)

    def time_open(self):
        if self.closed_at is None:
            self.closed_at = datetime.now(timezone.utc)

        return self.closed_at - self.created_at

    def time_open_sec(self):
        return self.time_open().total_seconds()

    def created_at_js(self):
        return int(time.mktime(self.created_at.timetuple())) * 1000

    def closed_at_js(self):
        return int(time.mktime(self.closed_at.timetuple())) * 1000

    def bugs(self):
        bugs = 0
        events = self.event_set.filter(event__in=['labeled', 'unlabeled'])

        for event in events:
            if event.event == 'labeled' and event.label == 'bug':
                bugs += 1

        return bugs

    def labels_duration(self):
        duration = {}
        events = self.event_set.filter(event='unlabeled')

        for event in events:
            if event.label in duration.keys():
                duration[event.label] += event.label_time()
            else:
                duration[event.label] = event.label_time()

        return duration

    def alert(self):
        if self.time_open() > timedelta(days=1):
            return 'danger'
        if self.time_open() > timedelta(hours=5):
            return 'warning'
        else:
            return 'success'

    def __str__(self):
        return self.title


class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE)
    event = models.CharField(max_length=30)
    label = models.CharField(max_length=30, null=True)
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True)

    def time_since_pr(self):
        return self.created_at - self.pull_request.created_at

    def label_time(self):
        if self.label is None or self.event == 'labeled':
            return None
        else:
            # find when the label was added
            label_added = Event.objects.filter(pull_request=self.pull_request, event='labeled', label=self.label,
                                               created_at__lte=self.created_at)[:1][0]
            return self.created_at - label_added.created_at

    def __str__(self):
        if self.label is None:
            label = ""
        else:
            label = self.label
        return "PR #{}: {} {}".format(self.pull_request.number, self.event, label)
