# -*- coding: utf-8 -*-
from django.core.management.base import LabelCommand
from django.db.models import Q

from contactBox.models import Message

from datetime import datetime, timedelta


class Command(LabelCommand):
    help = "Remind about Contact message"
    args = ''

    def handle(self, *options, **extras):
        yesterday = datetime.now() - timedelta(days=1)
        messages = Message.objects.filter(Q(notification_date__isnull=True) | Q(notification_date__lte=yesterday),
                                          unread=True)
        for m in messages:
            m.notify()
