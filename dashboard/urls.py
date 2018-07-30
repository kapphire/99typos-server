from django.urls import path, include
from rest_framework import routers
from dashboard import views

router = routers.DefaultRouter()
# router.signup('users', views.UserViewSet)

urlpatterns = [
    path('site/checker/celery/', views.CeleryTaskChecker.as_view(), name='site-checker-celery'),
    path('site/checker/celery/progress', views.CeleryTaskProgressChecker.as_view(), name='progress-checker-celery'),
]