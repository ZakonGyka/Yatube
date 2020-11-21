from django.contrib.auth.forms import forms
from django.forms import Textarea

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text', 'image',)
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
        help_texts = {
            'text': 'Поля со * обязательны для заполнения',
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'cols': 79, 'rows': 10}),
        }
        help_texts = {
            'text': 'Поля со * обязательны для заполнения',
        }
