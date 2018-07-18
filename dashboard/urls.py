from django.urls import path, include
from rest_framework import routers
from dashboard import views

router = routers.DefaultRouter()
# router.signup('users', views.UserViewSet)

urlpatterns = [
    path('site/register/', views.SiteRegister.as_view(), name='site-register'),
    path('site/list/', views.SiteList.as_view(), name='site-list'),
    path('site/check/', views.SiteCheck.as_view(), name='site-check'),
    path('site/checker/celery/', views.CeleryTaskChecker.as_view(), name='site-checker-celery'),
    path('page/list/', views.PageList.as_view(), name='page-list'),
    path('page/detail/', views.PageDetail.as_view(), name='page-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
]