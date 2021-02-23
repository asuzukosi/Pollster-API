from django.test import TestCase
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from .views import home, RegisterPollsterAPIView, pollsterFollowers, pollsterFollowing, followPollster, PollsterAPIView, unfollowPollster, PollsterDetailAPIView, ChoiceVotesAPIView, pollChartAPIView, LoginPollsterAPIView, ChoiceViewSet, PollsListCreateAPIView, PollsDetailAPIView, PollsTagsAPIView, RemoveTagFromPollAPIView
from .models import Pollster, Poll, Choice
from django.contrib.auth import get_user_model
import datetime
# Create your tests here.
from rest_framework.authtoken.models import Token


class PollsViewTests(APITestCase):

    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        self.client = APIClient()

    def test_OnlyLoggedInViewPolls(self):
        response = self.client.get('/api/polls/')
        self.assertEqual(response.status_code, 401, "Only logged in pollsters can view all polls")
        self.client.login(username="test", password="test")
        response = self.client.get('/api/polls/')
        self.assertEqual(response.status_code, 200, "Only logged in pollsters can view all polls")

    def test_OnlyLoggedInDetailsPolls(self):
        response = self.client.get('/api/polls/1/')
        self.assertEqual(response.status_code, 401, "Only logged in pollsters can view all polls")
        self.client.login(username="test", password="test")
        response = self.client.get('/api/polls/1/')
        self.assertEqual(response.status_code, 200, "Only logged in pollsters can view all polls")

    def test_OnlyOwnerCanEditOrDeletePoll(self):

        self.client.login(username='test2', password='test2')
        response = self.client.delete('/api/polls/1/')
        self.assertEqual(response.status_code, 400, "Only the owner of a poll can edit the poll")

        self.client.login(username='test', password='test')
        response = self.client.delete('/api/polls/1/')
        self.assertEqual(response.status_code, 204, "Only the owner of a poll can edit the poll")


class ChoiceViewTests(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_CreateChoice(self):
        self.client.login(username='test', password='test')
        params = {
            "text": "probably",
            "poll": 1
        }
        response = self.client.post('/api/polls/1/choices/', params)
        self.assertEqual(response.status_code, 201, "Poll can not have more than 5 choices")
        response = self.client.post('/api/polls/1/choices/', params)
        self.assertEqual(response.status_code, 400, "Poll can not have more than 5 choices")

    def test_EditChoice(self):
        params = {
            "text": "probably",
            "poll": 1
        }
        self.client.login(username='test2', password='test2')
        response = self.client.put('/api/polls/1/choices/1/', params)
        self.assertEqual(response.status_code, 403, "Only the creator of a choice can edit, view in detail or delete that choice")

        self.client.login(username='test', password='test')
        response = self.client.put('/api/polls/1/choices/1/', params)
        self.assertEqual(response.status_code, 200, "Only the creator of a choice can edit, view in detail or delete that choice")



class PollTagTest(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_OnlyACreatorCanAddViewRemoveTags(self):
        params = {
            'name': "swoosh"
        }
        self.client.login(username='test', password='test')
        response = self.client.post('/api/polls/1/tags/', params)
        self.assertEqual(response.status_code, 201, "Only the owner of the poll can add, remove or view tags")

        self.client.login(username='test2', password='test2')
        response = self.client.post('/api/polls/1/tags/', params)
        self.assertEqual(response.status_code, 403, "Only the owner of the poll can add, remove or view tags")


class VotingTest(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_VoteOnlyOnce(self):
        self.client.login(username='test2', password='test2')
        response = self.client.post('/api/polls/1/choices/1/votes/')
        self.assertEqual(response.status_code, 201, "Pollster can not vote for a poll twice")
        response = self.client.post('/api/polls/1/choices/1/votes/')
        self.assertEqual(response.status_code, 400, "Pollster can not vote for a poll twice")

    def test_OnlyLoggedInCanVote(self):
        response = self.client.post('/api/polls/1/choices/1/votes/')
        self.assertEqual(response.status_code, 401, "Only logged in pollsters can vote")


class TestPollChart(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_OnlyLoggedInCanGetChart(self):
        self.client.login(username='test2', password='test2')
        response = self.client.get('/api/polls/1/chart/')
        self.assertEqual(response.status_code, 200)

        self.client.login(username='test', password='test')
        response = self.client.get('/api/polls/1/chart/')
        self.assertEqual(response.status_code, 200)

class FollowUnfollowPollster(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_UserCanNotFollowSelf(self):
        self.client.login(username='test2', password='test2')
        response = self.client.get('/api/pollsters/1/follow/')
        self.assertEqual(response.status_code, 201, "You can not follow a pollster twice")
        response = self.client.get('/api/pollsters/1/follow/')
        self.assertEqual(response.status_code, 400, "You can not follow a pollster twice")

        response = self.client.get('/api/pollsters/2/follow/')
        self.assertEqual(response.status_code, 403, "You can not follow yourself")

    def test_UserCanNotUnfollowSelf(self):
        self.client.login(username='test2', password='test2')
        response = self.client.get('/api/pollsters/1/unfollow/')
        self.assertEqual(response.status_code, 400, "You can not unfollow someone you aren't following")
        response = self.client.get('/api/pollsters/1/follow/')
        response = self.client.get('/api/pollsters/1/unfollow/')
        self.assertEqual(response.status_code, 201, "You can not unfollow someone you aren't following")

        response = self.client.get("/api/pollsters/2/unfollow/")
        self.assertEqual(response.status_code, 403, "You can not unfollow yourself")

class TestPolster(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_OnlyLoggedInCanViewPollsters(self):
        response = self.client.get('/api/pollsters/')
        self.assertEqual(response.status_code, 401, "Only authenticated users can view list of pollsters")

        self.client.login(username='test', password='test')
        response = self.client.get('/api/pollsters/')
        self.assertEqual(response.status_code, 200, "Only authenticated users can view list of pollsters")

    def test_OnlyPollsterCanSeeSelfDetails(self):
        self.client.login(username='test2', password='test2')
        response = self.client.get('/api/pollsters/1/')
        self.assertEqual(response.status_code, 403, "A pollster can only see his/her personal details")

        response = self.client.get('/api/pollsters/2/')
        self.assertEqual(response.status_code, 200, "A pollster can only see his/her personal details")



class CheckFollowingAndFollowers(APITestCase):
    def setUp(self):
        self.pollster = Pollster(username="test", email="test@yahoo.com", password="test")
        self.pollster.set_password("test")
        self.pollster.save()

        self.pollster2 = Pollster(username="test2", email="test2@yahoo.com", password="test2")
        self.pollster2.set_password("test2")
        self.pollster2.save()

        poll = Poll(question="Are you logged in?", pollster=self.pollster, time_created=datetime.datetime.now())
        poll.save()
        choice = Choice(text="Yes", poll=poll)
        choice.save()
        choice = Choice(text="No", poll=poll)
        choice.save()
        choice = Choice(text="Maybe", poll=poll)
        choice.save()
        choice = Choice(text="Not sure", poll=poll)
        choice.save()
        # choice = Choice(text="Probably", poll=poll)
        # choice.save()
        self.poll = poll
        self.client = APIClient()

    def test_CheckFollowingAndFollowers(self):
        response = self.client.get('/api/pollsters/1/following/')
        self.assertEqual(response.status_code, 401)
        response = self.client.get('/api/pollsters/1/followers/')
        self.assertEqual(response.status_code, 401)

        self.client.login(username='test', password='test')
        response = self.client.get('/api/pollsters/1/following/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/pollsters/1/followers/')
        self.assertEqual(response.status_code, 200)


