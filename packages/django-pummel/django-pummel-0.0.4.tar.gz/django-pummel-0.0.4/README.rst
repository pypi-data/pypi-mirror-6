Django Pummel
=============
**Django app providing PML templates, tags and middleware.**

.. contents:: Contents
    :depth: 5


Usage
-----

Forms
~~~~~

Form fields, widgets and renderers are included so you can easily render forms. Forms should inherit from ``PMLForm`` and utilize included PML fields as illustrated by the following::

    from pml import forms

    class DemoForm(forms.PMLForm):
        submit_text = "Submit Text"
        text_field = forms.PMLTextField(
            label="Text Field Label",
            help_text="Text Field Help Text"
        )
        select_field = forms.PMLSelectField(
            label="Select Field Label",
            help_text="Select Field Help Text",
            choices=(
                ("value1", "select 1"),
                ("value2", "select 2"),
            )
        )
        checkbox_field = forms.PMLCheckBoxField(
            label="Check Box Field Label",
            help_text="Check Box Field Help Text",
            choices=(
                ("value1", "checkbox 1"),
                ("value2", "checkbox 2"),
            )
        )
        radio_field = forms.PMLRadioField(
            label="Radio Field Label",
            help_text="Radio Field Help Text",
            choices=(
                ("value1", "radio 1"),
                ("value2", "radio 2"),
            )
        )

You can then render the form by calling the following include in your template(which assumes a ``form`` context variable is available), i.e.::

    {% include 'pml/inclusion_tags/form.xml' %}

which will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/form.png

Middleware
~~~~~~~~~~

VLiveRemoteUserMiddleware
+++++++++++++++++++++++++

To automatically create and authenticate users using MSISDNs as provided by VLive include ``VLiveRemoteUserMiddleware`` and ``RemoteUserBackend`` in your settings, i.e::

    MIDDLEWARE_CLASSES = (
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'pml.middleware.VLiveRemoteUserMiddleware',
        ...
    )

    AUTHENTICATION_BACKENDS = (
        ...
        'django.contrib.auth.backends.RemoteUserBackend',
    )

With this setup ``VLiveRemoteUserMiddleware`` will detect the username in ``request.META['HTTP_X_UP_CALLING_LINE_ID']`` and will authenticate and auto-login that user using the ``RemoteUserBackend``.


RedirectMiddleware
++++++++++++++++++

PML requires an intermediary page when redirecting, conventional HTTP 302's are not supported. To automatically create this intermediary page include ``RedirectMiddleware`` as your first middleware class, i.e.::

    MIDDLEWARE_CLASSES = (
        'pml.middleware.RedirectMiddleware',
        ...
    )

With this setup all redirects will be intercepted and the ``pml/redirect.xml`` template will be rendered as a normal ``HttpResponse``, including `user messages <https://docs.djangoproject.com/en/dev/ref/contrib/messages/>`_ and PML redirect XML as created by the ``redirect`` tag (see below).


Inclusion Tags
~~~~~~~~~~~~~~

banner
++++++

Renders an image specified by ``image_url`` argument as a banner, i.e.::

    {% banner image_url='/url/to/image.png' %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/banner.png

The provided image should have a resolution of 241x60px. The Vodafone Live PML platform will resize it for specific devices.

divider
++++++

Renders a divider, i.e.::

    {% divider %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/divider.png

Headers are tandalone modules so you can not use them within other modules.

header
++++++

Renders a header bar with provided ``text`` and ``color``, i.e.::

    {% header text='Featured' color='pink' %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/header.png

Headers are standalone modules so you can not use them within other modules.


horizontal_links
++++++++++++++++

Renders horizontal links for collection of ``objects``. Link url and text is looked up from properties on individual objects as specified by the ``url_property`` and ``text_property`` arguments i.e.::

    {% horizontal_links objects=object_list url_property='get_absolute_url' text_property='title' %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/horizontal_links.png

link_list
+++++++++

Renders bulleted links for collection of ``objects``. Link url and text is looked up from properties on individual objects as specified by the ``url_property`` and ``text_property`` arguments i.e.::

    {% link_list objects=object_list url_property='get_absolute_url' text_property='title' %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/link_list.png


redirect
++++++++

Renders PML redirect XML causing a client side HTML redirect to provided ``url`` after the specified ``seconds`` i.e.::

    {% redirect seconds='2' url='http://www.google.com' %}

will render the following XML::

    <TIMER href="http://www.google.com" tenthsOfSecond="20"/>

If no ``url`` is provided ``request.META['HTTP_REFERER']`` will be used instead. ``redirect`` will only work if included before ``<VZV-DEFAULT>`` in your templates (if you extend from ``pml/base.xml`` include it as part of the ``header`` block) and your template contains other content (empty templates won't redirect).


text_module
+++++++++++

Renders evaluated HTML reformated for display within a PML ``<TEXT>`` element. The provided ``html`` is evaluated so you can specify tags and context variables is if you were creating normal Django template code, i.e.::

    {% text_module html='<b>bold</b><br /><a href="{{ object_url }}">link</a><br /><i>italic</i>' %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/text_module.png

thumbnail_html
++++++++++++++

Renders a thumbnail image followed by evaluated HTML reformated for display within a PML ``<TEXT>`` element. The provided ``html`` is evaluated so you can specify tags and context variables is if you were creating normal Django template code, i.e.::

    {% thumbnail_html image_url='/url/to/image.png' html='<b>bold</b><br /><a href="{{ object_url }}">link</a><br /><i>italic</i>' %}

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/thumbnail_html.png

thumbnail_include
+++++++++++++++++

Renders a thumbnail image followed by evaluated HTML reformated for display within a PML ``<TEXT>`` element, as included from the provided ``template`` argument. This should be used instead of ``thumbnail_html`` above if you need to include complex elements (i.e. other tags) that can't be included as part of other tags, i.e. ::

    {% thumbnail_include image_url='/url/to/image.png' template='path/to/template' %}

with the template containing::

    <b>bold</b><br />
    <a href="{{ object_url }}">link</a><br />
    <i>italic</i>

will render as

.. image:: https://github.com/praekelt/django-pummel/raw/develop/rst_media/thumbnail_html.png

.. note::

    All tags accept a ``color`` argument allowing you to specify background and link colors. Valid colors are orange, green, dove, marine, violet, red, black, grey, sand, pink, and darkred.

Templates
~~~~~~~~~

A ``pml/base.xml`` template is included from which you can ``extend`` as a starting point for your PML templates. The template includes a ``header`` and ``body`` block. You'll use the ``body`` block for the most of your content, but some tags like ``redirect`` needs to be placed in the ``header`` block.
