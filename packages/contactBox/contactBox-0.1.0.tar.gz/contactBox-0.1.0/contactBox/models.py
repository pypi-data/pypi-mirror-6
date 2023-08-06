# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from datetime import datetime


class Message(models.Model):
    date = models.DateTimeField(auto_now_add=True, help_text='Creation date')
    name = models.CharField('Name', max_length=255)
    email = models.EmailField('Email address')
    organization = models.CharField('Organization', max_length=255, blank=True)
    phone = models.CharField('Phone', blank=True, max_length=20)
    message = models.TextField('Comments')
    notification_date = models.DateTimeField(editable=False, blank=True, help_text='When notification was send',
                                             null=True)
    unread = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-id']

    def short(self):
        return self.message[:10] + '...'

    def notify(self):
        receivers = Receiver.objects.filter(active=True)
        if receivers.count():
            try:
                site = Site.objects.get_current()
                text_content = render_to_string('contactBox/email.txt',
                                                {'contact': self,
                                                'site': site, })
                msg = EmailMessage(
                    settings.EMAIL_SUBJECT_PREFIX + ' Contact',
                    text_content,
                    settings.EMAIL_FROM,
                    [r.email for r in receivers],
                    headers={'Reply-To': self.email}
                )
                msg.send(fail_silently=False)
                self.notification_date = datetime.now()
                self.save()
            except:
                pass


class Receiver(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name + ' (' + self.email + ')'
