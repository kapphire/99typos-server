import requests
from rest_framework import serializers
from invitations.models import Invitation


class InvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invitation
        fields = ('email',)
