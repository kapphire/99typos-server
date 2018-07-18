import os
import ast
import six
import binascii
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail.message import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
# Create your models here.

def _generate_code():
    return binascii.hexlify(os.urandom(20))


def send_multi_format_email(template_prefix, template_ctxt, target_email):
        subject_file = 'user_auth/%s_subject.txt' % template_prefix
        txt_file = 'user_auth/%s.txt' % template_prefix
        html_file = 'user_auth/%s.html' % template_prefix

        subject = render_to_string(subject_file).strip()
        from_email = settings.DEFAULT_EMAIL_FROM
        to = target_email
        bcc_email = settings.DEFAULT_EMAIL_BCC
        text_content = render_to_string(txt_file, template_ctxt)
        html_content = render_to_string(html_file, template_ctxt)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to], bcc=[bcc_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()


class CustomUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
        ),
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
            'Designates whether this user has completed the email verification process to allow login.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'    

    def __str__(self):
        return 'User: {}'.format(self.email)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)
        instance.save()


class SignupCodeManager(models.Manager):
    def create_signup_code(self, user):
        code = _generate_code()
        signup_code = self.create(user=user, code=code)
        return signup_code

    def set_user_is_verified(self, code):
        try:
            signup_code = SignupCode.objects.get(code=code)
            signup_code.user.is_verified = True
            signup_code.user.save()
            return True
        except SignupCode.DoesNotExist:
            pass
        return False


class AbstractBaseCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(_('code'), max_length=100, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def send_email(self, prefix):
        ctxt = {
            'email': self.user.email,
            'code': self.code
        }
        send_multi_format_email(prefix, ctxt, target_email=self.user.email)

    def __str__(self):
        return self.code


class SignupCode(AbstractBaseCode):
    objects = SignupCodeManager()
    
    def send_signup_email(self):
        prefix = 'signup_email'
        self.send_email(prefix)


class PasswordResetCodeManager(models.Manager):
    def create_reset_code(self, user):
        code = _generate_code()
        password_reset_code = self.create(user=user, code=code)
        return password_reset_code


class PasswordResetCode(AbstractBaseCode):
    objects = PasswordResetCodeManager()

    def send_password_reset_email(self):
        prefix = 'password_reset_email'
        self.send_email(prefix)

