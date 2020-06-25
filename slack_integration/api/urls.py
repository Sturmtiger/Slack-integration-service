from django.urls import path
from .views import (CreateUpdateDestroySlackMessageView,
                    InteractivityProcessingView)


urlpatterns = [
    path('message/', CreateUpdateDestroySlackMessageView.as_view(),
         name='slack-message'),
    path('interactivity/', InteractivityProcessingView.as_view()),
]
