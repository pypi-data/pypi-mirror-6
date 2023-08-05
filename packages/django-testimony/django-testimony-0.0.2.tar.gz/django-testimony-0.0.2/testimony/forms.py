from django.forms import widgets, ModelForm, Form, CharField, EmailField, TextInput, DecimalField, Textarea, IntegerField, DateField, TimeField, Select
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.contrib.localflavor.us.forms import USPhoneNumberField, USStateField, USZipCodeField, USStateSelect
from django.forms.extras.widgets import SelectDateWidget
import datetime
from django.template import Template, Context
from django.conf import settings  
from models import Testimonial



def sendEMail(self, site_email, body=None, subject=None, replyto=None):
    headers = {}
    
    if not body:
        format = ""
        for key in self.cleaned_data.keys():
            format += "%s: {{ %s }}\n" % (key, key)
        t = Template(format)
        body = t.render(Context(self.cleaned_data))
    
    if not subject:
        subject = 'Website feedback'
        
    if replyto:
        headers['Reply-To'] = replyto
        
    email_message = EmailMessage(
                                subject=subject,
                                body=body,
                                #from_email=site_email,
                                to=[site_email],
                                #connection=connection,
                                headers=headers,
                                #cc=['',]
                                )    

    ret = email_message.send(fail_silently=True)
    print ret


class TestimonialForm(ModelForm):
    
    class Meta:
        model = Testimonial
        exclude = ('date_given','published',)   

    def __init__(self, *args, **kwargs):
        super(TestimonialForm, self).__init__(*args, **kwargs)
                
        self.fields['author'].widget.attrs={'size':'51',} 
        self.fields['author'].label = "Your Name"
        self.fields['email'].widget.attrs={'size':'51',} 
        self.fields['email'].label = "Your email" 
        self.fields['poster_ip'].widget = widgets.HiddenInput()
        
    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        ip_address = kwargs.pop('ip_address', None)
        site_email = kwargs.pop('site_email', None)

        testimonial = super(TestimonialForm, self).save(commit=False)

        if ip_address:
            testimonial.poster_ip=ip_address
        
        if commit:
            testimonial.save()
        
            body = render_to_string("email_feedback.txt", {
                                                   'data': self.cleaned_data,
                                                   })
            subject = "SITE TESTIMONIAL"
            replyto = self.cleaned_data['email']
            sendEMail(self, site_email, body=body, subject=subject, replyto=replyto)

        
        return testimonial
    
