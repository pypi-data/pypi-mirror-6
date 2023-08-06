from django import forms
from suit_redactor.widgets import RedactorWidget

from .models import Article, Category


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'content': RedactorWidget(editor_options={
                'lang': 'en',
                'minHeight': '200',
                'buttons': [
                    'html', '|',
                    'bold', 'italic', 'deleted', 'underline', '|',
                    'unorderedlist', 'orderedlist', '|',
                    'alignleft', 'aligncenter', 'alignright', 'justify', '|',
                    'link'
                ]
            }),
        }


class ArticleSearchForm(forms.Form):
    """
    This is the article search form.
    """

    date_choices = []

    for date in Article.objects.dates('publish_on', 'month', order='DESC'):
        datestring = [date.strftime('%Y-%m'),date.strftime('%B %Y')]

        if datestring not in date_choices:
            date_choices.append(datestring)

    category = forms.ModelMultipleChoiceField(label="Category", queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    date = forms.MultipleChoiceField(label="Archive", choices=date_choices, widget=forms.CheckboxSelectMultiple(), required=False)