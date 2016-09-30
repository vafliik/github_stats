#get all weeks:
import datetime

import django
from django.utils import timezone


weeks = set()
d7 = datetime.timedelta( days = 7)
iterDay = datetime.date(2012,1,1)

print (iterDay.isocalendar()[1])

# while iterDay <= today:
#     weeks.add( iterDay.isocalendar()[1] )
#     iterDay += d7



#aggregate event by week
result = dict()
for w in weeks:
    result.setdefault( w ,0)
