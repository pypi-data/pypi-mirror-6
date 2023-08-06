# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.contrib import messages
from forms import ContactForm


class ContactFormView(TemplateView):
    form_class = ContactForm
    template_name = 'contact.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ContactFormView, self).get_context_data(*args, **kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        form = self.form_class(
            data=request.POST,
        )
        if form.is_valid():
            form.save()
            context['saved'] = True
            messages.add_message(request, messages.INFO, 'Your message has been sent.')
            form = self.form_class()
        context['form'] = form
        return self.render_to_response(context)
