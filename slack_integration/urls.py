from django.urls import path
from . import views

urlpatterns = [
    path('', views.AppListView.as_view(), name='app_list'),
    path('app-registration/', views.CreateAppView.as_view(),
         name='app_registration'),
    path('app-update/<pk>/', views.UpdateAppView.as_view(), name='app_update'),
    path('app/<pk>/', views.AppDetailView.as_view(), name='app_detail'),
    path('template-create/<app_pk>/', views.CreateTemplateView.as_view(),
         name='template_create'),
    path('template/<pk>/', views.TemplateDetailView.as_view(),
         name='template_detail'),
    path('template-update/<pk>/', views.UpdateTemplateView.as_view(),
         name='template_update'),
    path('actions-block-create/<template_pk>/',
         views.CreateActionsBlockView.as_view(),
         name='actions_block_create'),
    path('actions-block-detail/<pk>/', views.ActionsBlockDetailView.as_view(),
         name='actions-block-detail'),
    path('actions-block-update/<pk>/', views.UpdateActionsBlockView.as_view(),
         name='actions-block-update'),
]
