from django.urls import path, include
from rest_framework import routers
from websites import views

router = routers.DefaultRouter()

urlpatterns = [
    path('site/register/', views.SiteRegister.as_view(), name='site-register'),
    path('site/list/', views.SiteList.as_view(), name='site-list'),
    path('site/check/', views.SiteCheck.as_view(), name='site-check'),
    path('site/change/<uuid:id>', views.ChangeSite.as_view(), name='change-site'),
    path('page/list/', views.PageList.as_view(), name='page-list'),
    path('page/detail/', views.PageDetail.as_view(), name='page-detail'),
]