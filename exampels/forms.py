from django import forms


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label="آپلود فایل CSV")
    # file = forms.FileField()
