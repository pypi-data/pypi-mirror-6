Welcome to django-gollum
========================

This is **django-gollum**, a better way to mess with styling Django forms. gollum provides a better way to specify just the HTML Attributes and CSS classes you need on a Form subclass.

Installation
------------

To install django-gollum, just use::

    pip install django-gollum


Dependencies
------------

* Python version
    * django-gollum is tested on Python 2.7 and Python 3.3.
    * It is probable that it will run on Python 2.6, but Python 2.6 is not
      explicitly tested.
* Django version
    * django-gollum is tested against Django 1.4+ on Python 2.7, and Django
      1.5+ on Python 3.3.
* Other dependencies
    * `dict.sorted`_
    * `six`_

All dependencies are handled for you if you install using pip.

.. _dict.sorted: https://github.com/lukesneeringer/dict-sorted.git
.. _six: https://pythonhosted.org/six/

Getting Started
---------------

Adding HTML or CSS to a Django Form with gollum is easy:

  1. Subclass `gollum.forms.Form` or `gollum.forms.ModelForm`.
  2. Add a Attrs or CSS inner class specifying fields with extra HTML attributes or CSS, respectively.

Here's an example::

    from gollum import forms

    class MyForm(forms.Form):
        foo = models.CharField(max_length=50)
        bar = models.IntegerField()

        class Attrs:
            bar = { 'placeholder': 25 }

        class CSS:
            foo = 'green'
            bar = ['purple', 'translucent']


When this form is rendered in the template, the "foo" ``<input>`` tag will have the "green" CSS class applied, and the "bar" ``<input>`` will have both "purple" and "translucent" applied. Additionally, the "bar" ``<input>`` would have ``placeholder="25"`` set as an HTML attribute.

Getting Help
------------

If you think you've found a bug in django-pgfields itself, please post an
issue on the `Issue Tracker`_.

For usage help, you're free to e-mail the author, who will provide help (on
a best effort basis) if possible.

.. _Issue Tracker: https://github.com/lukesneeringer/django-gollum/issues

License
-------

New BSD


Index
-----

.. toctree::

    usage
    html
    css
    settings
