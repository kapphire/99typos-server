from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny

from invitations.models import Invitation
from invitations.forms import CleanEmailMixin
from invitations.exceptions import AlreadyAccepted, AlreadyInvited, UserRegisteredEmail

from .serializers import InvitationSerializer


class InviteUser(APIView):
    permission_classes = (AllowAny,)
    serializer_class = InvitationSerializer

    def get_object(self):
        try:
            return Invitation.objects.get(id=id)
        except Invitation.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        emails = list(set(request.data))
        # response = {'valid': [], 'invalid': []}
        response = list()
        for email in emails:
            email = email.strip()
            try:
                validate_email(email)
                CleanEmailMixin().validate_invitation(email)
                invite = Invitation.create(email)
            except(ValueError, KeyError):
                pass
            except(ValidationError):
                pass
                # response['invalid'].append({email: 'invalid email'})
            except(AlreadyAccepted):
                pass
                # response['invalid'].append({email: 'already accepted'})
            except(AlreadyInvited):
                pass
                # response['invalid'].append({email: 'pending invite'})
            except(UserRegisteredEmail):
                pass
                # response['invalid'].append({email: 'user registered email'})
            else:
                # invite.send_invitation(request)
                response.append(invite)
        serializer = self.serializer_class(response, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)