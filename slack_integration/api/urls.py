from django.urls import path
from .views import PostMessageView, UpdateMessageView, DeleteMessageView


urlpatterns = [
    path('send-message/', PostMessageView.as_view()),
    path('update-message/', UpdateMessageView.as_view()),
    path('delete-message/', DeleteMessageView.as_view()),
]
