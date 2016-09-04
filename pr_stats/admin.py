from django.contrib import admin

from pr_stats.models import PullRequest, Event, User

admin.site.register(PullRequest)
admin.site.register(Event)
admin.site.register(User)
