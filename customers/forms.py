import uuid

from django import forms
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from customers.models import Customer


class CustomerForm(forms.ModelForm):
    api_key = forms.CharField(required=False)
    contact_address = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Customer
        fields = (
            'customer_type',
            'company_name',
            'contact_name',
            'contact_mail',
            'contact_phone',
            'contact_address',
            'comments',
            'api_key',
        )

    def send_email(self):
        sender = settings.DEFAULT_FROM_EMAIL
        recipient = self.cleaned_data.get('contact_mail', '')
        subject = 'pressureNET Data API'
        content = render_to_string('customers/email/registration.html', {
            'customer': self.instance,
        })

        email = EmailMultiAlternatives(subject, '', sender, [recipient])
        email.attach_alternative(content, 'text/html')
        email.send()

    def clean(self):
        cleaned_data = super(CustomerForm, self).clean()

        # Generate API Key
        api_key = uuid.uuid4().get_hex()

        cleaned_data['api_key'] = api_key

        return cleaned_data

    def save(self, *args, **kwargs):
        super(CustomerForm, self).save(*args, **kwargs)
        self.send_email()
