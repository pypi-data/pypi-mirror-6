from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.mail import send_mail

from wattup.forms import ContactForm


class ContactView(FormView):

    template_name = 'wattup/contact.html'
    form_class = ContactForm
    success_url = '/thanks/'

    def form_valid(self, form):
        cd = form.cleaned_data
        send_mail(
            '(' + settings.ORG_NAME + '): ' + cd['name'] + ' -(origin)- ' + cd['sender'],
            cd['words'],
            cd.get('email', settings.DEFAULT_FROM_EMAIL),
            [settings.DEFAULT_TO_EMAIL],
            fail_silently=False,
        )
        return HttpResponseRedirect('/thanks/')


def thanks(request):
    return render(request, 'wattup/thanks.html')
