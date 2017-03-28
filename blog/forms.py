from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}),
        max_length=60)

    class Meta:
        model = Post
        fields = ('title', 'text',)


class UserForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('username', 'password',)
        exclude = ('email',)


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}),
        max_length=60)
    password = forms.CharField(widget=forms.PasswordInput(
        render_value=False, attrs={'class': 'form-control'}),
        min_length=6, max_length=60)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]
        exclude = ('email',)


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        label='Comment')

    class Meta:
        model = Comment
        fields = ('text',)
        exclude = ('author',)
