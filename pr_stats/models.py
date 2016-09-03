from datetime import datetime, timezone, timedelta

from django.db import models

from pr_stats import services


class PullRequest(models.Model):
    number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    state = models.CharField(max_length=30)
    body = models.TextField(default='')
    created_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    def time_open(self):
        if self.closed_at is None:
            self.closed_at = datetime.now(timezone.utc)

        return self.closed_at - self.created_at

    def time_open_sec(self):
        return self.time_open().total_seconds()

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

    def __str__(self):
        if self.label is None:
            label = ""
        else:
            label = self.label
        return "PR #{}: {} {}".format(self.pull_request.number, self.event, label)
