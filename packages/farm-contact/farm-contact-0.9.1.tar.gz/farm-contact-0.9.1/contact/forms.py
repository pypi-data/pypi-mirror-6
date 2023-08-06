from .models import Enquiry, EnquiryType
from django import forms
from django.forms import ModelForm


class EnquiryForm(ModelForm):

    name = forms.CharField(
        label='Your Name',
        widget=forms.TextInput(attrs={'required':''})
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.TextInput(attrs={'required':''})
    )
    phone = forms.CharField(
        label='Phone Number'
    )
    enquiry_type = forms.ModelChoiceField(
        queryset=EnquiryType.objects.all(),
        label='I am a',
        widget=forms.Select(attrs={'required':''})
    )
    message = forms.CharField(
        label='How can we help you?',
        widget=forms.Textarea(attrs={'required':''})
    )

    class Meta:
        model = Enquiry
        exclude = ['ip']

    def save(self, commit=True, ip=None):
        instance = super(ModelForm, self).save(False)
        instance.ip = ip
        if commit:
            instance.save()
        return instance
