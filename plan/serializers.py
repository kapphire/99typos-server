import requests
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PlanCharge
from user_auth.models import User

User = get_user_model()


class PlanConfirmSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanCharge
        fields = ('id', 'tier', 'charge_id', 'user')

    def create(self, data):
        validated_data = {
            'tier': data['tier'],
            'charge_id': data['charge_id'],
            'user': User.objects.get(id=data['user']),
        }
        plan = PlanCharge(**validated_data)
        plan.save()
        return plan