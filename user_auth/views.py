import string
import random

#Django Libs
from django.contrib.auth import login, logout as django_logout
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import redirect
from django.utils.translation import gettext as _

#Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import (
    User, 
    SignupCode,
    PasswordResetCode
)

#Serializers
from .serializers import (
    CreateUserSerializer,
    ReturnUserSerializer,
    PasswordResetSerializer  ,
    PasswordResetVerifiedSerializer  
)

User = get_user_model()

def token_generator(size=5, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup(request):
    serialized = CreateUserSerializer(data=request.data)
    if serialized.is_valid():
        user = serialized.create(request.data)
        signup_code = SignupCode.objects.create_signup_code(user)
        signup_code.send_signup_email()
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class SignupVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        code = request.GET.get('code', '')
        verified = SignupCode.objects.set_user_is_verified(code)

        if verified:
            try:
                signup_code = SignupCode.objects.get(code=code)
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass
            content = {'success': _('User verified.')}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'detail': _('Unable to verify user.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ReturnUserSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(email=email, password=password)

            if user and user.is_verified:
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key}, status=status.HTTP_200_OK)
                else:
                    content = {'detail': _('User account not active.')}
                    return Response(content, status=status.HTTP_401_UNAUTHORIZED)
            else:
                content = {'detail': _('Unable to login with provided credentials.')}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        """
        Remove all auth tokens owned by request.user.
        """
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        content = {'success': _('User logged out.')}
        return Response(content, status=status.HTTP_200_OK)


class PasswordReset(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            try:
                user = get_user_model().objects.get(email=email)
                if user.is_verified and user.is_active:
                    password_reset_code = PasswordResetCode.objects.create_reset_code(user)
                    password_reset_code.send_password_reset_email()
                    content = {'email': email}
                    return Response(content, status=status.HTTP_201_CREATED)

            except get_user_model().DoesNotExist:
                content = {'detail': _("The user doesn't exist.")}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            # Since this is AllowAny, don't give away error.
            content = {'detail': _('Password reset not allowed.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetVerify(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        code = request.GET.get('code', '')
        try:
            password_reset_code = PasswordResetCode.objects.get(code=code)
            content = {'success': _('User verified.')}
            status = 'true'
        except PasswordResetCode.DoesNotExist:
            content = {'detail': _('Unable to verify user.')}
            status = 'false'
        return redirect(("http://52.14.232.117/password/reset/verify?code={}&status={}").format(code, status))
            

class PasswordResetVerified(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetVerifiedSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            code = serializer.data['code']
            password = serializer.data['password']

            try:
                password_reset_code = PasswordResetCode.objects.get(code=code)
                password_reset_code.user.set_password(password)
                password_reset_code.user.save()
                content = {'success': _('Password reset.')}
                return Response(content, status=status.HTTP_200_OK)
            except PasswordResetCode.DoesNotExist:
                content = {'detail': _('Unable to verify user.')}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


