from django.urls import path, include
from rest_framework import routers
from users import views

router = routers.DefaultRouter()

urlpatterns = [
    path('users/<str:token>', views.UserList.as_view(), name='user-list'),
    path('user/change/<int:id>', views.UserChange.as_view(), name='user-change')
]