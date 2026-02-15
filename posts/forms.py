from django import forms
from django.forms import modelformset_factory

from .models import Post, PostImage

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
