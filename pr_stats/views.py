import logging

import dateutil.parser

from datetime import datetime, timezone, timedelta
from django.db.models import Min, F, Max, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from pr_stats import services
from pr_stats.models import PullRequest, Event, User
from pr_stats.services import median_value, create_user_if_not_already, get_all_pulls, update_pulls



def index(request):
    pr_list = PullRequest.objects.order_by('-number')
    context = {
        'pr_list': pr_list,
    }
    return render(request, 'pr_stats/index.html', context)


def detail(request, pr_number):
    pr = get_object_or_404(PullRequest, pk=pr_number)
    events = pr.event_set.all()

    context = {'pr': pr, 'events': events}
    return render(request, 'pr_stats/detail.html', context)


def statistics(request):
    pulls = PullRequest.objects.filter(state='closed')
    fastest_pr = pulls.order_by('closed_after_sec')[:1]
    slowest_pr = pulls.order_by('-closed_after_sec')[:1]
    average_time = pulls.aggregate(Avg('closed_after_sec'))['closed_after_sec__avg']
    median_time = median_value(pulls, 'closed_after_sec')
    context = {
        'pulls': pulls,
        'fastest_pr': fastest_pr[0],
        'slowest_pr': slowest_pr[0],
        'average_time': timedelta(seconds=average_time),
        'median_time': timedelta(seconds=median_time)
    }
    return render(request, 'pr_stats/statisticts.html', context)


def pulls(request):
    # get_all_pulls()

    last_update = PullRequest.objects.aggregate(Max('updated_at'))['updated_at__max']\

    buffer_time = last_update - timedelta(minutes=15)

    update_pulls(buffer_time.isoformat())

    return redirect('pr_stats:index')

