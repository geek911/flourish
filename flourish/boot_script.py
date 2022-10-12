from django.contrib.auth.models import Group

try:
    Group.objects.get(name='assign manager')
except Group.DoesNotExist:
    Group.objects.create(name='assign manager')

try:
    Group.objects.get(name='Recruiters')
except Group.DoesNotExist:
    Group.objects.create(name='Recruiters')