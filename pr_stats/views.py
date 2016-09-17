import logging

import dateutil.parser

from datetime import datetime, timezone, timedelta, date

import django
from django.db.models import Min, F, Max, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from pr_stats.models import PullRequest, Event, User
from pr_stats.services import create_user_if_not_already, get_all_pulls, update_pulls
from pr_stats.statistics import median_value, pr_with_most_bugs


def index(request):
    pr_list = PullRequest.objects.order_by('-number')
    context = {
        'pr_list': pr_list,
    }
    return render(request, 'pr_stats/index.html', context)


def detail(request, pr_number):
    pr = get_object_or_404(PullRequest, pk=pr_number)

    events = pr.event_set.filter(event__in=['labeled', 'unlabeled'])

    context = {'pr': pr, 'events': events}
    return render(request, 'pr_stats/detail.html', context)


def statistics(request, year=None, month=None, day=None):
    today = django.utils.timezone.now()
    this_monday = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    if year:
        year = int(year)
        month = int(month)
        day = int(day)
        start = django.utils.timezone.now().replace(year=year, month=month, day=day, hour=0, minute=0, second=0,
                                                    microsecond=0)
    else:
        start = this_monday

    end = (start + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=99)

    previous = start - timedelta(days=7)
    next = start + timedelta(days=7)

    query_filter = {'created_at__gte': start, 'created_at__lt': end}

    open_pulls = PullRequest.objects.filter(**query_filter, **{'state': 'open'})
    closed_pulls = PullRequest.objects.filter(**query_filter, **{'state': 'closed'})
    fastest_pr = closed_pulls.order_by('closed_after_sec')[:1]
    slowest_pr = closed_pulls.order_by('-closed_after_sec')[:1]
    average_time = closed_pulls.aggregate(Avg('closed_after_sec'))['closed_after_sec__avg']
    median_time = median_value(closed_pulls, 'closed_after_sec') if closed_pulls else 0
    context = {
        'pulls': closed_pulls,
        'open_pulls': open_pulls,
        'query_filter': query_filter,
        'previous': previous,
        'current': this_monday,
        'next': next,
    }
    if closed_pulls.exists():
        context['fastest_pr'] = fastest_pr[0]
        context['slowest_pr'] = slowest_pr[0]
        context['average_time'] = timedelta(seconds=average_time)
        context['median_time'] = timedelta(seconds=median_time)

    context['longest_open'] = open_pulls.order_by('created_at')[:1][0] if open_pulls else None
    context['most_bugs'] = pr_with_most_bugs(closed_pulls)

    return render(request, 'pr_stats/statisticts.html', context)


def pulls(request):
    last_update = PullRequest.objects.aggregate(Max('updated_at'))['updated_at__max']
    if last_update is not None:
        buffer_time = last_update - timedelta(minutes=15)

        update_pulls(buffer_time.isoformat())

    else:
        update_pulls()

    return redirect('pr_stats:index')


def pulls_all(request, q):
    update_pulls(q=q)

    return redirect('pr_stats:index')
