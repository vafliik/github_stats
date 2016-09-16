from django.contrib import admin

from pr_stats.models import PullRequest, Event, User

class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'state', 'created_at')
    list_display_links = ('number', 'title')

admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(Event)
admin.site.register(User)
