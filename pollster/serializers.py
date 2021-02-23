from rest_framework import serializers
from .models import Pollster, Poll, Topic, Vote, Choice, Follow
from rest_framework.authtoken.models import Token


class PollsterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pollster
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]

        pollster = Pollster(username=username, email=email)
        pollster.set_password(validated_data["password"])
        pollster.save()
        token = Token(user=pollster)
        token.save()

        return pollster


class PollSerializer(serializers.ModelSerializer):
    pollster = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    choices = serializers.StringRelatedField(many=True)

    class Meta:
        model = Poll
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class ChoiceDetailSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True)

    class Meta:
        model = Choice
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class PollDetailSerializer(serializers.ModelSerializer):
    pollster = PollsterSerializer()
    tags = TopicSerializer(many=True)
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Poll
        fields = '__all__'

        extra_kwargs = {
            "pollster": {
                "read_only": True
            }
        }


class PollsterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pollster
        fields = '__all__'
