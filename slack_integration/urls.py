from django.urls import path
from . import views

urlpatterns = [
    path('', views.AppListView.as_view(), name='app_list'),
    path('app-registration/', views.AppRegistrationView.as_view(),
         name='app_registration'),
    path('app/<pk>/', views.AppDetailView.as_view(), name='app_detail'),
    path('template-create/<app_pk>/', views.CreateTemplateView.as_view(),
         name='template_create'),
    path('template/<pk>/', views.TemplateDetailView.as_view(),
         name='template_detail'),
]
