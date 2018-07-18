from django.urls import path, include
from rest_framework import routers
from user_auth import views

router = routers.DefaultRouter()
# router.signup('users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', views.signup, name='signup'),
    path('signup/verify/', views.SignupVerify.as_view(), name='signup-verify'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('password/reset/', views.PasswordReset.as_view(), name='password-reset'),
    path('password/reset/verify/', views.PasswordResetVerify.as_view(), name='password-reset-verify'),
    path('password/reset/verified/', views.PasswordResetVerified.as_view(), name='password-reset-verified'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]