from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget


class UploadFileForm(forms.Form):
    txt_file = forms.FileField()


class DateRangeForm(forms.Form):
    start_date = JalaliDateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    end_date = JalaliDateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
