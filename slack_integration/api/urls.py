from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (CreateUpdateDestroySlackMessageView, SlackEventsView,
                    InteractivityProcessingView, SlackApplicationViewSet,)


urlpatterns = [
    path('message/', CreateUpdateDestroySlackMessageView.as_view(),
         name='slack-message'),
    path('interactivity/', InteractivityProcessingView.as_view()),
    path('events/', SlackEventsView.as_view()),
]

router = DefaultRouter()
router.register('applications', SlackApplicationViewSet)

urlpatterns += router.urls
