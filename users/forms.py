from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    avatar = forms.ImageField(required=False)

    '''
    class Meta:
        model = CustomUser
        fields = ('username', 'email')
    '''
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'avatar', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user