=====
FORMS-SMOQ
=====
Forms-SmoQ django is a simple application that contains useful forms
for use in django.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Install pip install django-forms-smoq
2. Add "forms-smoq" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'forms-smoq',
    )
3. Import the form where you want.

Configuration
-----------
GENERIC_DEFAULT_MODEL = If we have a generic model of a foreign key is
a model by default, the form will create a selection list.
We write "app_label.Model"

GENERIC_%s_MODEL % YOUR_MODEL = If you are using forms in several different
models, we can insert the exact form in which the model is to use what model.
Instead YOUR_MODEL enter the model name of which it is applicable.
We write "app_label.Model"