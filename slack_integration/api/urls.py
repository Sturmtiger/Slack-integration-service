from django.urls import path
from .views import (CreateUpdateDestroySlackMessageView, SlackEventsView,
                    InteractivityProcessingView)


urlpatterns = [
    path('message/', CreateUpdateDestroySlackMessageView.as_view(),
         name='slack-message'),
    path('interactivity/', InteractivityProcessingView.as_view()),
    path('events/', SlackEventsView.as_view()),
]
