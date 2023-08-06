Settings
========

gollum exposes a small number of settings that you can apply to get
certain global behaviors on gollum forms.

FORM_REQUIRED_CSS_CLASS
-----------------------

* Default: *(not set)*
* Type: ``str``

If specified, the given CSS class will be added to every required field
on every gollum form.

FORM_ERROR_CSS_CLASS
--------------------

* Default: *(not set)*
* Type: ``str``

If specified, the given CSS class will be added to every field that is
in an error state on every gollum form.

FORM_REQUIRED_ATTRS
-------------------

* Default: *(not set)*
* Type: ``dict``

If specified, the given HTML attributes will be applied to every required
field on every gollum form.

Example::

    FORM_REQUIRED_ATTRS = { 'required': 'true' }

FORM_OPTIONAL_ATTRS
-------------------

* Default: *(not set)*
* Type: ``dict``

If specified, the given HTML attributes will be applied to every field
that is *not* required on any gollum form.

Example::

    FORM_OPTIONAL_ATTRS = { 'placeholder': 'Optional' }

FORM_GLOBAL_ATTRS
-----------------

* Default: *(not set)*
* Type: ``dict``

If specified, the given HTML attributes will be applied to *every* form
field on every gollum form.
