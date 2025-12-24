from django import forms
from django.contrib.auth import authenticate
from core.models import Question, Answer, Tag
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        user = authenticate(
            username=cleaned.get('username'),
            password=cleaned.get('password')
        )
        if not user:
            raise forms.ValidationError("Неверный логин или пароль")
        cleaned['user'] = user
        return cleaned

class SignupForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data['password'] != data['password2']:
            raise forms.ValidationError("Пароли не совпадают")
        return data

class AskQuestionForm(forms.Form):
    title = forms.CharField(max_length=200)
    detailed = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(required=False)

    def clean_tags(self):
        tags = [t.strip() for t in self.cleaned_data['tags'].split(',') if t.strip()]
        if len(tags) > 3:
            raise forms.ValidationError("Максимум 3 тега")
        return tags

class AnswerForm(forms.Form):
    answer_text = forms.CharField(widget=forms.Textarea)
