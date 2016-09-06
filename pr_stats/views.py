import dateutil.parser
from datetime import timedelta
from django.db.models import Min, F, Max, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from pr_stats import services
from pr_stats.models import PullRequest, Event, User
from pr_stats.services import median_value, create_user_if_not_already, save_pulls


def index(request):
    pr_list = PullRequest.objects.order_by('-number')
    context = {
        'pr_list': pr_list,
    }
    return render(request, 'pr_stats/index.html', context)


def detail(request, pr_number):
    pr = get_object_or_404(PullRequest, pk=pr_number)
    events = pr.event_set.all()

    if not events:
        event_data = services.get_events(pr.number)

        for event in event_data:
            e = Event(pull_request=pr)
            e.id = event['id']
            e.event = event['event']
            e.label = event['label']['name'] if 'label' in event.keys() else None
            e.actor = create_user_if_not_already(event['actor'])
            e.created_at = dateutil.parser.parse(event['created_at'])
            e.save()

        events = pr.event_set.all()

    context = {'pr': pr, 'events': events}
    return render(request, 'pr_stats/detail.html', context)


def statistics(request):
    state = request.GET.get('state', None)
    pulls = PullRequest.objects.filter(state='closed')
    fastest_pr = pulls.order_by('closed_after_sec')[:1]
    slowest_pr = pulls.order_by('-closed_after_sec')[:1]
    average_time = pulls.aggregate(Avg('closed_after_sec'))['closed_after_sec__avg']
    median_time = median_value(pulls, 'closed_after_sec')
    context = {
        'argument': state,
        'pulls': pulls,
        'fastest_pr': fastest_pr[0],
        'slowest_pr': slowest_pr[0],
        'average_time': timedelta(seconds=average_time),
        'median_time': timedelta(seconds=median_time)
    }
    return render(request, 'pr_stats/statisticts.html', context)


def pulls(request):
    save_pulls()

    return redirect('pr_stats:index')

