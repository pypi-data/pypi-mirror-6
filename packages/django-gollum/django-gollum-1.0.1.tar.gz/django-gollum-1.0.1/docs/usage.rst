Using django-gollum
===================

In order to use gollum, you must use gollum's ``Form`` and ``ModelForm``
superclass, rather than the ones that ship with Django.

This is extremely important: nothing documented here will work unless
the gollum Form classes are superclasses of your form. This also gives
you the ability to opt-in to gollum forms on an as-needed basis, if you
prefer.

The easiest way to do this is just to import your ``forms`` module from
``gollum`` rather than ``django``::

    from gollum import forms

    class MyGollumForm(forms.Form):
        [...]

It's that simple. Read on to learn how to make use of what gollum provides.
The next topic is `specifying HTML attributes <html.html>`_.
