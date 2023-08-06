Specifying HTML Attributes
==========================

In Form Classes
---------------

gollum gives you the ability to specify HTML attributes easily on a form
class. You can specify HTML attributes on any number of fields on your form
by using an ``Attrs`` inner class within your form::

    from gollum import forms

    class MyGollumForm(forms.Form):
        foo = forms.IntegerField()
        bar = forms.IntegerField()

        class Attrs:
            foo = { 'disabled': 'true' }

The above code will cause the form, when rendered, to add a ``disabled="true"``
HTML attribute to the ``foo`` field (but do nothing to the ``bar`` field).

A common use-case for this, if you're using HTML5 forms, is to set a
`placeholder attribute`_. This causes the browser to display default text
in the input field until it gains focus::

    from gollum import forms

    class UserForm(forms.Form):
        first_name = forms.CharField(max_length=30)
        last_name = forms.CharField(max_length=30)
        email = forms.EmailField(max_length=75)
        phone = forms.CharField(max_length=15, required=False)

        class Attrs:
            phone = { 'placeholder': 'Optional' }

.. _placeholder attribute: http://davidwalsh.name/html5-placeholder

This code would cause the phone widget to look like this:

.. code-block:: html

    <input name="phone" id="id_phone" type="text" placeholder="optional">


In Templates
------------

Even though the Django documentation only exposes a way to set attributes
`in form widgets themselves`_, one could argue that a better place for
HTML attribute information to live is in the template itself, especially
since a form could be used in different templates and need different
attributes set.

gollum does not expose a special mechanism to do this (yet). However, this
can be accomplished by directly calling the ``as_widget`` method of
a bound field in Django.

The problem: ``as_widget`` takes arguments, so you'll either need to write
a template tag to send the necessary arguments to it, or use a template
language that supports arguments (such as `Jinja`_).

Here's a quick sample of the latter option:

.. code-block:: jinja

    {% for field in user_form %}
        {{ field.as_widget(attrs={ 'placeholder': field.label }) }}
    {% endfor %}

This method allows you not to specify HTML attributes on your form class at
all, and may be preferable, especially if the HTML attributes change depending
on where the form is rendered.

.. _in form widgets themselves: https://docs.djangoproject.com/en/1.5/ref/forms/widgets/#django.forms.Widget.attrs
.. _Jinja: http://jinja.pocoo.org/


CSS
---

It would be possible to specify CSS classes in this way, by writing directly
to the ``class`` HTML attribute. But don't; gollum also exposes a way to
`specify CSS classes <css.html>`_.
