import dateutil.parser
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from pr_stats import services
from pr_stats.models import PullRequest, Event


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
            e = Event(pull_request = pr)
            e.id = event['id']
            e.event = event['event']
            e.label = event['label']['name'] if 'label' in event.keys() else None
            e.save()

        events = pr.event_set.all()

    context = {'pr': pr, 'events': events}
    return render(request, 'pr_stats/detail.html', context)

def pulls(request):
    PullRequest.objects.all().delete()
    Event.objects.all().delete()

    data = services.get_pulls()
    for pull in data:
        pr = PullRequest()
        pr.number = pull['number']
        pr.title = pull['title']
        pr.state = pull['state']
        pr.body = pull['body']
        pr.created_at = dateutil.parser.parse(pull['created_at'])

        if pull['closed_at'] is not None:
            pr.closed_at = dateutil.parser.parse(pull['closed_at'])

        pr.save()

        # event_data = services.get_events(pr.number)
        #
        # for event in event_data:
        #     e = Event(pull_request = pr)
        #     e.id = event['id']
        #     e.event = event['event']
        #     e.label = event['label']['name'] if 'label' in event.keys() else None
        #     e.save()

    return redirect('pr_stats:index')
