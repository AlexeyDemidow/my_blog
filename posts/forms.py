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

# Formset для изображений (до 5 файлов например)
PostImageFormSet = modelformset_factory(
    PostImage,
    fields=('image',),
    extra=5,
    widgets={'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': False})}
)
