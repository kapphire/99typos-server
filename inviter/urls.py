from django.urls import path, include
from rest_framework import routers
from inviter import views

router = routers.DefaultRouter()

urlpatterns = [
    path('invite/', views.InviteUser.as_view(), name='invite-user')
]