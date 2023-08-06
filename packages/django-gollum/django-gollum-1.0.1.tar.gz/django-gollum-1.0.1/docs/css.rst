Specifying CSS Classes
======================

Much like HTML attributes, gollum provides a way to specify CSS classes
both in forms and also exposes a new way to do so in templates.

However, unlike HTML attributes, where the most recent attribute specified
wins, the CSS class specification understands to take the union of any CSS
classes sent to it. That makes it preferable to use this mechanism rather
than specifying ``class`` as an HTML attribute directly.

In Form Classes
---------------

In order to specify a CSS class on a form, declare a ``CSS`` inner class
in your ``Form`` class, and specify any classes to apply::

    from gollum import forms

    class MyForm(forms.Form):
        foo = models.CharField(max_length=50)
        bar = models.IntegerField()

        class CSS:
            foo = {'spam', 'eggs'}

The above code, when rendered in an template, will cause the ``<input>`` tag
for the ``foo`` field to have two CSS classes: ``spam`` and ``eggs``.

You can specify CSS classes here using a list, set, or tuple. You can also
use a string if you have only one CSS class, or you can even use a
space-separated string like you would in actual HTML markup.

The following CSS inner-class is identical to the one in the example above::

    class CSS:
        foo = 'spam eggs'

Order of class specification doesn't matter; it'll be normalized to a
Python ``set``, which is unordered. Duplicate classes don't matter either,
for the same reason.

In Templates
------------

It may be preferable for your use case to specify CSS classes in templates
rather than in the form itself. (This does seem like where such information
naturally belongs.)

Again, like in `HTML Attributes <html.html#in-templates>`_, the solution is
the ``as_widget`` method. The story's a little different this time, though:
Django doesn't provide a clean way to specify CSS classes, so gollum
actually subclasses BoundField to provide one.

That mechanism is the ``css_classes`` keyword argument:

.. code-block:: jinja

    {% for field in form %}
        {{ field.as_widget(css_classes='myclass') }}
    {% endfor %}

Much like the specification above, you can send a list (or other, similar
iterable) or a string, and gollum will do the right thing.
