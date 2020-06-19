from django.urls import path
from .views import CreateUpdateDestroySlackMessageView


urlpatterns = [
    path('slack-message/', CreateUpdateDestroySlackMessageView.as_view()),
]
