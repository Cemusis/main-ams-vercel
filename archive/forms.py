from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

# Login form with email and password
class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'input-field'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'input-field',
            'id': 'password'
        })
    )
    remember = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # store request for authentication
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')

        if email and password:
            # Authenticate email as username
            user = authenticate(request=self.request, username=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password")

            cleaned['user'] = user
        return cleaned
