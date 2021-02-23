from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from .models import Poll, Pollster


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user.id == view.kwargs["pk"]:
            return True
        else:
            return False


class IsOwnerChoice(BasePermission):
    def has_permission(self, request, view):

        poll = Poll.objects.get(pk=view.kwargs["ppk"])
        if request.user == poll.pollster:
            return True
        else:
            return False


class NotSelf(BasePermission):
    def has_permission(self, request, view):
        pollster = Pollster.objects.get(pk=view.kwargs["pk"])
        if request.user == pollster:
            return False
        else:
            return True
