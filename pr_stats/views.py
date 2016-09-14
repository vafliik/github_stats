import logging

import dateutil.parser

from datetime import datetime, timezone, timedelta, date

import django
from django.db.models import Min, F, Max, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

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


def statistics(request, year=None, month=None, day=None):
    if year:
        year = int(year)
        month = int(month)
        day = int(day)
        start = django.utils.timezone.now().replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
    else:
        today = django.utils.timezone.now()
        this_monday = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        start = this_monday

    end = (start + timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=99)

    previous = start - timedelta(days=7)
    next = start + timedelta(days=7)

    query_filter = {'state': 'closed', 'created_at__gte': start, 'created_at__lt': end}

    pulls = PullRequest.objects.filter(**query_filter)
    fastest_pr = pulls.order_by('closed_after_sec')[:1]
    slowest_pr = pulls.order_by('-closed_after_sec')[:1]
    average_time = pulls.aggregate(Avg('closed_after_sec'))['closed_after_sec__avg']
    median_time = median_value(pulls, 'closed_after_sec')
    context = {
        'pulls': pulls,
        'query_filter': query_filter,
        'previous': previous,
        'next': next,
        'fastest_pr': fastest_pr[0],
        'slowest_pr': slowest_pr[0],
        'average_time': timedelta(seconds=average_time),
        'median_time': timedelta(seconds=median_time)
    }
    return render(request, 'pr_stats/statisticts.html', context)


def pulls(request):
    last_update = PullRequest.objects.aggregate(Max('updated_at'))['updated_at__max']
    if last_update is not None:
        buffer_time = last_update - timedelta(minutes=15)

        update_pulls(buffer_time.isoformat())

    else:
        update_pulls()

    return redirect('pr_stats:index')

def pulls_all(request):

    update_pulls()

    return redirect('pr_stats:index')
