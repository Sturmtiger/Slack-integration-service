from django.urls import path
from .views import PostMessageView


urlpatterns = [
    path('send-message/', PostMessageView.as_view()),
]
