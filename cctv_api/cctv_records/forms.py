from django import forms


class UploadReportForm(forms.Form):
    file = forms.FileField()
