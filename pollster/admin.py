from django.contrib import admin
from .models import Pollster, Topic, Poll, Choice, Follow, Vote

# Register your models here.
admin.site.register(Pollster)
admin.site.register(Topic)
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Follow)
admin.site.register(Vote)

