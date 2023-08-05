django-botscout
===============

This provides an easy hook into the Botscout system for Django forms

Available Settings
------------------

.. code:: python

    # All settings are optional. They are displayed here with their defaults
    BOTSCOUT_API_KEY = None
    BOTSCOUT_API_URL = 'http://botscout.com/test/'
    BOTSCOUT_CACHE_TIMEOUT = 1800
    BOTSCOUT_NETWORK_TIMEOUT = 5

Additionally, you can set the following variables on individual forms to
alter their behavior:

.. code:: python

    BOTSCOUT_NAME_FIELD = 'name'
    BOTSCOUT_EMAIL_FIELD = 'email'
    BOTSCOUT_ERROR_MESSAGE = 'This request was matched in the BotScout database'

Basic Usage
-----------

In forms.py:

.. code:: python

    from botscout import BotScoutForm
    from django import forms


    class ContactForm(BotScoutForm, forms.Form):
        name = forms.CharField('Name')
        email = forms.EmailField('Email')

In views.py:

.. code:: python

    from .forms import ContactForm


    def contact(request):
        if request.method == 'POST':
            form = ContactForm(request=request, data=request.POST)
            if form.is_valid():
                ...
        else:
            form = ContactForm(request=request)
        ...

Advanced Usage
--------------

.. code:: python

    from botscout import BotScoutForm
    from django import forms
    from django.db import models


    class Person(models.Model):
        full_name = models.CharField('Full name', max_length=255)
        email_address = models.EmailField('Email')


    class MyForm(BotScoutForm, forms.ModelForm):
        BOTSCOUT_NAME_FIELD = 'full_name'
        BOTSCOUT_EMAIL_FIELD = 'email_address'
        BOTSCOUT_ERROR_MESSAGE = 'GO AWAY SPAM BOT!'

        class Meta:
            model = Person
