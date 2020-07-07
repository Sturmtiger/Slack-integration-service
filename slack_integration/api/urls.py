from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    path('message/', views.CreateUpdateDestroySlackMessageView.as_view(),
         name='slack-message'),
    path('interactivity/', views.InteractivityProcessingView.as_view()),
    path('events/', views.SlackEventsView.as_view()),
    path('templates/<pk>/crontab/', views.TemplateCrontabView.as_view()),
]

router = DefaultRouter()
router.register('applications', views.SlackApplicationViewSet)
router.register('templates', views.TemplateViewSet)
router.register('actions-blocks', views.ActionsBlockViewSet)
router.register('buttons', views.ButtonViewSet)

urlpatterns += router.urls
