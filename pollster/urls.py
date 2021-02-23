from django.urls import path, include
from .views import home, RegisterPollsterAPIView, pollsterFollowers, TestView, pollsterFollowing, followPollster, PollsterAPIView, unfollowPollster, PollsterDetailAPIView, ChoiceVotesAPIView, pollChartAPIView, LoginPollsterAPIView, ChoiceViewSet, PollsListCreateAPIView, PollsDetailAPIView, PollsTagsAPIView, RemoveTagFromPollAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('choices', ChoiceViewSet, basename='Choices')
urlpatterns = [
    path('', home, name='Home'),
    path('register/', RegisterPollsterAPIView.as_view(), name='Register'),
    path('login/', LoginPollsterAPIView.as_view(), name='Login'),
    path('polls/', PollsListCreateAPIView.as_view(), name='Polls'),
    path('polls/<int:pk>/', PollsDetailAPIView.as_view(), name='Poll'),
    path('polls/<int:pk>/chart/', pollChartAPIView, name='Poll Chart'),
    path('polls/<int:pk>/tags/', PollsTagsAPIView.as_view(), name='PollTags'),
    path('polls/<int:pk>/tags/<int:t_pk>/', RemoveTagFromPollAPIView.as_view(), name='PollTagsDelete'),
    path('polls/<int:ppk>/', include(router.urls)),
    path('polls/<int:pk>/choices/<int:c_pk>/votes/', ChoiceVotesAPIView.as_view(), name='PollChoiceVotes'),
    path('pollsters/', PollsterAPIView.as_view(), name='Pollster'),
    path('pollsters/<int:pk>/', PollsterDetailAPIView.as_view(), name='Pollster Detail'),
    path('pollsters/<int:pk>/follow/', followPollster, name='Follow Pollster'),
    path('pollsters/<int:pk>/unfollow/', unfollowPollster, name='Unfollow Pollster'),
    path('pollsters/<int:pk>/followers/', pollsterFollowers, name='Pollster Followers'),
    path('pollsters/<int:pk>/following/', pollsterFollowing, name='Pollster Following'),
    path('test/', TestView.as_view(), name="Test")
]