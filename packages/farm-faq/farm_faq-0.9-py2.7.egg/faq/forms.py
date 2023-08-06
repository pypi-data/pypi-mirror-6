from django.forms import ModelForm
from suit_redactor.widgets import RedactorWidget

class QuestionAdminForm(ModelForm):
    class Meta:
        widgets = {
            'answer': RedactorWidget(editor_options={
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
