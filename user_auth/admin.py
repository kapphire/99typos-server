from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from .forms import UserChangeForm, UserCreationForm
from .models import (
    SignupCode,
    PasswordResetCode
)

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'is_superuser', 'is_active', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')


class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')


admin.site.register(User, UserAdmin)
admin.site.register(SignupCode, SignupCodeAdmin)
admin.site.register(PasswordResetCode, PasswordResetCodeAdmin)