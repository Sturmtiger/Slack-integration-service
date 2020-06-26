from django.urls import path
from . import views

urlpatterns = [
    path('', views.AppListView.as_view(), name='app-list'),

    path('app-registration/', views.CreateAppView.as_view(),
         name='app-registration'),
    path('app-update/<pk>/', views.UpdateAppView.as_view(), name='app-update'),
    path('app/<pk>/', views.AppDetailView.as_view(), name='app-detail'),
    path('app-delete/<pk>/', views.DeleteAppView.as_view(), name='app-delete'),

    path('template-create/<app_pk>/', views.CreateTemplateView.as_view(),
         name='template-create'),
    path('template/<pk>/', views.TemplateDetailView.as_view(),
         name='template-detail'),
    path('template-update/<pk>/', views.UpdateTemplateView.as_view(),
         name='template-update'),
    path('template-delete/<pk>/', views.DeleteTemplateView.as_view(),
         name='template-delete'),

    path('actions-block-create/<template_pk>/',
         views.CreateActionsBlockView.as_view(),
         name='actions-block-create'),
    path('actions-block/<pk>/', views.ActionsBlockDetailView.as_view(),
         name='actions-block-detail'),
    path('actions-block-update/<pk>/', views.UpdateActionsBlockView.as_view(),
         name='actions-block-update'),
    path('actions-block-delete/<pk>/', views.DeleteActionsBlockView.as_view(),
         name='actions-block-delete'),
]
