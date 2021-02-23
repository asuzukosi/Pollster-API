from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.views import APIView
from .models import Pollster, Poll, Topic, Choice, Vote, Follow
from .serializers import PollsterSerializer, PollSerializer, FollowSerializer, PollsterDetailSerializer, VoteSerializer, PollDetailSerializer, TopicSerializer, ChoiceSerializer
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner, IsOwnerChoice, NotSelf
import datetime


def home(request):
    return HttpResponse("Hello from the pollster api")


class RegisterPollsterAPIView(CreateAPIView):
    queryset = Pollster.objects.all()
    serializer_class = PollsterSerializer
    lookup_field = 'pk'


class LoginPollsterAPIView(APIView):

    def post(self, request):
        user = authenticate(username=request.data["username"], password=request.data["password"])
        if user:
            token = user.auth_token.key
            return Response({
                "token": token
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "No user with that set of user credentials found"
            }, status=status.HTTP_400_BAD_REQUEST)


class PollsListCreateAPIView(ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Poll.objects.all()
    lookup_field = 'pk'
    serializer_class = PollSerializer


class PollsDetailAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Poll.objects.all()
    serializer_class = PollDetailSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if request.user == poll.pollster:
            return self.update(request, *args, **kwargs)
        else:
            return Response({
                "error": "You can not edit another pollsters poll"
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if request.user == poll.pollster:
            return self.destroy(request, *args, **kwargs)
        else:
            return Response({
                "error": "You can not delete another pollsters poll"
            }, status=status.HTTP_400_BAD_REQUEST)


class PollsTagsAPIView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsOwner]

    def get(self, request, pk):
        poll = Poll.objects.get(pk=pk)
        tags = poll.tags
        serializer = TopicSerializer(tags, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        poll = Poll.objects.get(pk=pk)
        serializer = TopicSerializer(data=request.data)

        if serializer.is_valid():
            try:
                topic = Topic.objects.get(name=serializer.validated_data["name"])
                poll.tags.add(topic)
                poll.save()

                tags = poll.tags
                serializer = TopicSerializer(tags, many=True)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Topic.DoesNotExist:
                topic = serializer.save()
                poll.tags.add(topic)
                poll.save()

                tags = poll.tags
                serializer = TopicSerializer(tags, many=True)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            Response({
                "error": "Invalid Tag data, please enter proper tag data"
            }, status=status.HTTP_400_BAD_REQUEST)


class RemoveTagFromPollAPIView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsOwner]

    def delete(self, request, pk, t_pk):
        try:
            poll = Poll.objects.get(pk=pk)
            tag = Topic.objects.get(pk=t_pk)

        except:
            return Response({
                "error": "Tag or poll with such an id does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        poll.tags.remove(tag)
        poll.save()

        tags = poll.tags
        serializer = TopicSerializer(tags, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChoiceViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsOwnerChoice]

    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        choices = Choice.objects.filter(poll_id=self.kwargs["ppk"])
        return choices

    def create(self, request, *args, **kwargs):
        if int(request.data["poll"]) != int(self.kwargs["ppk"]):
            print(request.data["poll"])
            print(self.kwargs["ppk"])
            return Response({
                "you can not create choice for a different poll"
            }, status=status.HTTP_400_BAD_REQUEST)

        poll = Poll.objects.get(pk=self.kwargs["ppk"])
        choices = poll.choices.all()
        if len(choices) >= 5:
            return Response({
                "you can not have more than 5 choices in a poll"
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        data = request.data
        if int(data["poll"]) != int(self.kwargs["ppk"]):
            print(request.data["poll"])
            print(self.kwargs["ppk"])
            return Response({
                "you can not update choice for a different poll"
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)


class ChoiceVotesAPIView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, c_pk):
        votes = Vote.objects.filter(poll_id=pk, choice_id=c_pk)
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, c_pk):
        user = request.user
        poll = Poll.objects.get(pk=pk)
        choice = Choice.objects.get(pk=c_pk)
        try:
            vote = Vote.objects.get(pollster=user, poll=poll)
            return Response({
                "error": "Pollster can not vote twice"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Vote.DoesNotExist:
            vote = Vote(pollster=user, poll=poll, choice=choice, time_voted=datetime.datetime.now())
            vote.save()
            serializer = VoteSerializer(vote)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def pollChartAPIView(request, pk):

    if request.method == 'GET':
        labels = []
        values = []

        try:
            poll = Poll.objects.get(pk=pk)
            choices = poll.choices.all()

        except:
            return Response({
                "error": "Invalid url values, poll or choice does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        for choice in choices:
            labels.append(choice.text)
            values.append(len(choice.votes.all()))

        return Response({
            "labels": labels,
            "values": values
        }, status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PollsterAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    queryset = Pollster.objects.all()
    serializer_class = PollsterSerializer
    lookup_field = 'pk'


class PollsterDetailAPIView(RetrieveAPIView):
    permission_classes = [IsOwner]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    queryset = Pollster.objects.all()
    serializer_class = PollsterDetailSerializer
    lookup_field = 'pk'


@api_view(['GET'])
@permission_classes([NotSelf])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def followPollster(request, pk):
    if request.method == 'GET':
        pollster = Pollster.objects.get(pk=pk)
        user = request.user
        try:
            follow = Follow.objects.get(pollster=user, followed=pollster)
            return Response({
                "error": "You are already following this pollster"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Follow.DoesNotExist:
            follow = Follow(pollster=user, followed=pollster, time=datetime.datetime.now())
            follow.save()
            return Response({
                "message": f"You have successfully followed {pollster.username}"
            }, status=status.HTTP_201_CREATED)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([NotSelf])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def unfollowPollster(request, pk):
    if request.method == 'GET':
        pollster = Pollster.objects.get(pk=pk)
        user = request.user
        try:
            follow = Follow.objects.get(pollster=user, followed=pollster)

        except:
            return Response({
                "error": "You can not unfollow someone you aren't following"
            }, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()
        return Response({
            "message": f"You have successfully followed {pollster.username}"
         }, status=status.HTTP_201_CREATED)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def pollsterFollowers(request, pk):
    if request.method == 'GET':
        pollster = Pollster.objects.get(pk=pk)
        follows = pollster.followed
        serializer = FollowSerializer(follows, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def pollsterFollowing(request, pk):
    if request.method == 'GET':
        pollster = Pollster.objects.get(pk=pk)
        follows = pollster.follows
        serializer = FollowSerializer(follows, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        Response(status=status.HTTP_400_BAD_REQUEST)


class TestView(GenericAPIView):

    def get(self, request):
        return Response({
            "msg": "This is a generic api view"
        }, status=status.HTTP_200_OK)
