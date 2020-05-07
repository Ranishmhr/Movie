from django import forms
from django.contrib.auth import (
authenticate,
get_user_model,
login,
logout
)
from django.core.validators import validate_email
from movies.models import Ratings

User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control",'placeholder': 'Username'}),label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control",'placeholder': 'Password'}),label='')

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect passsword")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
            return super(UserLoginForm, self).clean(*args, **kwargs)

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Username'}),
                               label='')
    email = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Email'}),
                               label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Password'}),
                               label='')
    Confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': 'Retype Password'}),
                               label='')

    def clean(self):

        cleaned_data = self.cleaned_data
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = cleaned_data.get("password")
        passwordrepeat = cleaned_data.get("Confirm_password")
        if password != passwordrepeat:
            raise forms.ValidationError("Passwords must match.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User exists")
        return cleaned_data

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]

class ReviewForm(forms.ModelForm):
    class Meta:
        model=Ratings
        fields=["comment",
        "rating"
        ]