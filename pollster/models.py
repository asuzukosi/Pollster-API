from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Pollster(AbstractUser):
    interests = models.ManyToManyField(Topic, related_name='people_interested')
    bio = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pollster = models.ForeignKey(Pollster, related_name='polls', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Topic, related_name='tagged_polls', null=True, blank=True)
    time_created = models.DateTimeField()

    def __str__(self):
        return self.question


class Choice(models.Model):
    text = models.CharField(max_length=100)
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Vote(models.Model):
    pollster = models.ForeignKey(Pollster, related_name='voted', on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, related_name='votes', on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, related_name='votes', on_delete=models.CASCADE)
    time_voted = models.DateTimeField()

    def __str__(self):
        return f'{self.pollster} voted for {self.choice} in poll {self.poll}'


class Follow(models.Model):
    pollster = models.ForeignKey(Pollster, related_name='followed', on_delete=models.CASCADE)
    followed = models.ForeignKey(Pollster, related_name='follows', on_delete=models.CASCADE)
    time = models.DateTimeField()

    def __str__(self):
        return f'{self.pollster} followed {self.followed}'












