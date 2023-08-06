Django CKEd
===========

A django application that use django-cked as texteditor. It update RichTextField with config parameter

For more informations about django-cked follow this link: https://bitbucket.org/ssbb/django-cked/overview

**IMPORTANT! The application is no longer supported. Please do not use it!

**CKEditor and elFinder integration for Django Framework.**

Provides a ``RichTextField`` and ``CKEditorWidget`` with upload and
browse support.

|CKEditor| |elFinder|

Installation
------------

::

    pip install twentytab-cked


Configuration
-------------

Add ``cked`` to your ``INSTALLED_APPS`` setting.

Then set ``ELFINDER_OPTIONS`` in your settings:

::

    ELFINDER_OPTIONS = {
        ## required options
        'root': os.path.join(PROJECT_ROOT, 'media', 'uploads'),
        'URL': '/media/uploads/',
    }

And add CKEd URL include to your project ``urls.py`` file:

::

    url(r'^cked/', include('cked.urls')),

Settings
--------

-  **CKEDITOR\_OPTIONS**: CKEditor config. See
   http://docs.ckeditor.com/#!/guide/dev_configuration
-  **ELFINDER\_OPTIONS**: elFinder config. See
   https://github.com/Studio-42/elFinder/wiki/Client-configuration-options

Usage
-----

Model field
~~~~~~~~~~~

::

    from django.db import models
    from cked.fields import RichTextField

    EASY_CKE = {
        'height': 200,
        'width':400,
        'forcePasteAsPlainText': True,
        'toolbar': [['Bold', 'Italic', 'Underline', '-',
                     'JustifyLeft', 'JustifyCenter', 'JustifyRight',
                     'JustifyBlock', '-', 'Link', 'Unlink', '-', 'Source']],
    }

    class Entry(models.Model):
        text = RichTextField(config=EASY_CKE)

Widget
~~~~~~

::

    from django import forms
    from cked.widgets import CKEditorWidget

    class MyForm(forms.Form):
        text = forms.CharField(widget=CKEditorWidget)

**NOTE**: If you are using custom forms, dont’r forget to include form
media to your template:

::

    {{ form.media }}

.. |CKEditor| image:: https://bitbucket.org/ssbb/django-cked/raw/default/img/ckeditor.jpg
.. |elFinder| image:: https://bitbucket.org/ssbb/django-cked/raw/default/img/elfinder.jpg
