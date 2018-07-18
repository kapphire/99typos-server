import json, stripe
from urllib.parse import urlparse

#Django Libs
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render

#Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import PlanCharge

#Serializers
from .serializers import PlanConfirmSerializer

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


# Create your views here.
class PlanConfirm(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PlanConfirmSerializer

    def post(self, request, format=None):
        user_token = request.data.get('userToken')
        stripe_token = request.data.get('stripeToken')
        amount = request.data.get('amount')
        tier = request.data.get('tier')
        user = Token.objects.get(key=user_token).user
        
        if user.is_verified:
            charge = stripe.Charge.create(
                amount = amount,
                currency = "usd",
                source = stripe_token,
                description = "The plan charged to the user"
            )
            data = {
                'tier': tier,
                'charge_id': charge.id,
                'user': user.id
            }
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            plan = serializer.create(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
