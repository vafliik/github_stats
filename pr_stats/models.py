from datetime import datetime, timezone

from django.db import models

from pr_stats import services


class PullRequest(models.Model):
    number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    state = models.CharField(max_length=30)
    body = models.TextField(default='')
    created_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    def duration(self):
        if self.closed_at is None:
            self.closed_at = datetime.now(timezone.utc)

        return self.closed_at - self.created_at

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
