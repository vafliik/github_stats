from django.contrib import admin

from pr_stats.models import PullRequest, Event

admin.site.register(PullRequest)
admin.site.register(Event)
