
from django import forms

from slugfield import SlugFormField

from test_app.models import Article


class ArticleModelForm(forms.ModelForm):
    class Meta:
        model = Article


class ArticleForm(forms.Form):
    name = forms.CharField(max_length=100)
    slug = SlugFormField(populate_from='name')
