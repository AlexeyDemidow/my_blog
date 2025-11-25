# forms.py
from django import forms
from .models import Post, PostImage
from django.forms import modelformset_factory

class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'})
        }

PostImageFormSet = modelformset_factory(
    PostImage,
    fields=("image",),
    extra=1,
    can_delete=True
)
