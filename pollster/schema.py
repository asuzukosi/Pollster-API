import graphene
from graphene_django import DjangoObjectType
from graphene_django.rest_framework.mutation import SerializerMutation
from .models import Poll, Choice, Vote, Pollster, Topic, Follow
from .serializers import PollsterSerializer
from django.http import Http404
import datetime


class TopicType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = ['id', 'name']


class VoteType(DjangoObjectType):
    class Meta:
        model = Choice
        fields = '__all__'


class ChoiceType(DjangoObjectType):
    class Meta:
        model = Choice
        fields = '__all__'

    votes = graphene.Int()

    def resolve_votes(self, info):
        return len(Vote.objects.filter(choice=self))


class PollOwnerType(DjangoObjectType):
    class Meta:
        model = Pollster
        fields = ['id', 'username']


class PollType(DjangoObjectType):
    class Meta:
        model = Poll
        fields = '__all__'

    choices = graphene.List(ChoiceType)
    pollster = graphene.Field(PollOwnerType)
    votes = graphene.Int()
    tags = graphene.List(TopicType)

    def resolve_tags(self, info):
        return Topic.objects.filter(tagged_polls=self)

    def resolve_votes(self, info):
        return len(Vote.objects.filter(poll=self))

    def resolve_choices(self, info):
        return Choice.objects.filter(poll=self)

    def resolve_pollster(self, info):
        return self.pollster


class PollstersPollType(DjangoObjectType):
    class Meta:
        model = Poll
        fields = '__all__'

    votes = graphene.Int()

    def resolve_votes(self, info):
        return len(Vote.objects.filter(poll=self))


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = '__all__'


class PollsterType(DjangoObjectType):
    class Meta:
        model = Pollster
        fields = '__all__'

    polls = graphene.List(PollstersPollType)
    followers = graphene.List(FollowType)
    following = graphene.List(FollowType)

    def resolve_polls(self, info):
        return Poll.objects.filter(pollster=self)

    def resolve_followers(self, info):
        return Follow.objects.filter(followed=self)

    def resolve_following(self, info):
        return Follow.objects.filter(pollster=self)


class CreatePoll(graphene.Mutation):
    class Arguments:
        question = graphene.String()
        pollster = graphene.String()

    poll = graphene.Field(PollType)

    @classmethod
    def mutate(cls, root, info, question, pollster):
        print(question)
        print(pollster)
        pollster = Pollster.objects.get(pk=pollster)
        poll = Poll(pollster=pollster, question=question, time_created=datetime.datetime.now())
        poll.save()

        return CreatePoll(poll=poll)


class AddChoice(graphene.Mutation):
    class Arguments:
        text = graphene.String()
        poll = graphene.String()

    choice = graphene.Field(ChoiceType)

    @classmethod
    def mutate(cls, root, info, text, poll):
        poll = Poll.objects.get(pk=poll)
        if info.context.user != poll.pollster:
            return Http404
        if len(poll.choices.all()) >= 5:
            return Http404

        choice = Choice(text=text, poll=poll)
        choice.save()

        return AddChoice(choice=choice)


class DeletePoll(graphene.Mutation):
    class Arguments:
        poll_id = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, poll_id):
        poll = Poll.objects.get(pk=poll_id)
        if info.context.user != poll.pollster:
            return Http404
        poll.delete()
        return DeletePoll(ok=True)


class RemoveChoice(graphene.Mutation):
    class Arguments:
        poll_id = graphene.String()
        choice_id = graphene.String()

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, poll_id, choice_id):
        poll = Poll.objects.get(pk=poll_id)
        choice = Choice.objects.get(pk=choice_id)

        if choice.poll != poll:
            return RemoveChoice(message="This choice does not belong to this poll")

        if poll.pollster != info.context.user:
            return RemoveChoice(message="You do not have permission to carry out this action")

        choice.delete()
        return RemoveChoice(message="Successful")


class Query(graphene.ObjectType):
    polls = graphene.List(PollType)
    poll = graphene.Field(PollType, pk=graphene.String())
    pollsters = graphene.List(PollsterType)

    def resolve_polls(self, info):
        return Poll.objects.all()

    def resolve_poll(self, info, pk):
        return Poll.objects.get(pk=pk)

    def resolve_pollsters(self, info):
        return Pollster.objects.all()


class Mutation(graphene.ObjectType):
    create_poll = CreatePoll.Field()
    add_choice = AddChoice.Field()
    delete_poll = DeletePoll.Field()
    remove_choice = RemoveChoice.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

