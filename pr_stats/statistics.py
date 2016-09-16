import json
import logging
import os

import dateutil.parser
import requests

from pr_stats.models import PullRequest, User, Event

logger = logging.getLogger("statistics")

def median_value(queryset, term):
    count = queryset.count()
    values = queryset.values_list(term, flat=True).order_by(term)
    if count % 2 == 1:
        return values[int(round(count / 2))]
    else:
        return sum(values[count / 2 - 1:count / 2 + 1]) / 2.0

def pr_with_most_bugs(pr_queryset):
    bugs, pr = 0, None
    for item in pr_queryset:
        if item.bugs() > bugs:
            bugs, pr = item.bugs(), item
    return bugs, pr