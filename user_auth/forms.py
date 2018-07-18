from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2


class UserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(label="Password",
                                         help_text="Raw passwords are not stored, so there is no way to see "
                                                   "this user's password, but you can change the password "
                                                   "using <a href=\"password/\">this form</a>.")

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        return self.initial.get('password')
