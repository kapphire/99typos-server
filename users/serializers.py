import requests
from django.contrib.auth import get_user_model
from rest_framework import serializers
from user_auth.models import User
from websites.serializers import SiteSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    sites = SiteSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'sites')
