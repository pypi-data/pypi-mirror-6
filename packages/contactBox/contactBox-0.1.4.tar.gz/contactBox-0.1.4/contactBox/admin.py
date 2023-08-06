# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.util import unquote
from models import Message, Receiver


class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'organization', 'notification_date')
    readonly_fields = ('date',)
    list_filter = ('unread', 'date',)

    def title(self, obj):
        style = 'bold' if obj.unread else 'normal'
        return '<span style="font-weight: %s;">%s</span>' % (style, obj.date)
    title.allow_tags = True
    title.admin_order_field = 'date'

    def change_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if obj is not None and not request.method == 'POST':
            obj.unread = False
            obj.save()

        return super(MessageAdmin, self).change_view(request, object_id,
                                                     extra_context=extra_context)

admin.site.register(Message, MessageAdmin)
admin.site.register(Receiver)
