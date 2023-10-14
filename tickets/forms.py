from django import forms
from .models import Comment, Ticket
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField


class CloseTicketForm(forms.Form):
    STATUS_CHOICES = (
        ('open', 'باز'),
        ('close', 'بسته'),
    )
    close_reason = forms.ChoiceField(choices=STATUS_CHOICES, label='Status')


class TicketForm(forms.ModelForm):
    attachment = MultiFileField(min_num=1, max_num=5,
                                max_file_size=1024 * 1024 * 5)  # تعریف فیلد attachment به عنوان غیرضروری

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'priority', 'attachment',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
