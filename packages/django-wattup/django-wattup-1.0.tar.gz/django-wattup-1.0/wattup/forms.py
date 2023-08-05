from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=20)
    sender = forms.EmailField(max_length=40, label='Email')
    words = forms.CharField(widget=forms.Textarea)