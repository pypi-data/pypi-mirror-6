***********
Contact Box
***********

.. image:: https://travis-ci.org/ArabellaTech/contactBox.png?branch=master
   :target: https://travis-ci.org/ArabellaTech/contactBox

.. image:: https://coveralls.io/repos/ArabellaTech/contactBox/badge.png?branch=master
  :target: https://coveralls.io/r/ArabellaTech/contactBox?branch=master



To use as standard contact form replacement

.. contents::

Requirements
============

Django configured properly for sending emails. Sites framework.
Cron support - check conf.cron.

Settings
========

EMAIL_FROM

SITE_ID


Usage
=====

Add contactBox into INSTALLED_APPS in settings.py.

in views.py:

::

    from contactBox.views import ContactFormView
    from contactBox.forms import ContactForm


    class ContactView(ContactFormView):
        template_name = 'contact.html'
        form_class = ContactForm

Please also check:

https://github.com/YD-Technology/contactBox/blob/master/contactBox/views.py

https://github.com/YD-Technology/contactBox/blob/master/test_project/templates/contact.html
