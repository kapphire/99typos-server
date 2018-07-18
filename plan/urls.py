from django.urls import path, include
from rest_framework import routers
from plan import views

router = routers.DefaultRouter()
# router.signup('users', views.UserViewSet)

urlpatterns = [
    path('plan/confirm/', views.PlanConfirm.as_view(), name='plan-confirm')
]