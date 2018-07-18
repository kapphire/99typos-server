from django.contrib.auth import password_validation as validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SignupCode

User = get_user_model()

class CreateUserSerializer(serializers.HyperlinkedModelSerializer):    
    confirm_password = serializers.CharField()
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def validate_email(self, email):
        existing = User.objects.filter(email=email).first()
        if existing:
            try:
                signup_code = SignupCode.objects.get(user=existing)
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass
            raise serializers.ValidationError("Someone with that email address has already registered. Was it you?")
        return email

    def validate(self, data):
        errors = dict()
        if not data.get('password') or not data.get('confirm_password'):
            raise serializers.ValidationError("Please enter a password and confirm it.")

        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        try:
            validators.validate_password(password=data.get('password'), user=User)
        except ValidationError as e:
             errors['password'] = list(e.messages)
        if errors:
             raise serializers.ValidationError(errors)
        return data

    def create(self, data):
        validated_data = {
            'email': data['email'],
            'password': data['password']
        }
        user = User.objects.create_user(**validated_data)
        return user


class ReturnUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)


class PasswordResetVerifiedSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)