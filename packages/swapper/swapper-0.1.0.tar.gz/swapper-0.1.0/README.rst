Swapper
=======

Django Swappable Models - No longer only for auth.User!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Swapper is an unofficial API for the undocumented but very powerful
Django feature: swappable models. Swapper facilitates implementing
arbitrary swappable models in your own reusable apps.

Example Use Case
----------------

Suppose your reusable app has two related tables:

.. code:: python

    from django.db import models
    class Parent(models.Model):
        name = models.TextField()

    class Child(models.Model):
        name = models.TextField()
        parent = models.ForeignKey(Parent)

Suppose further that you want to allow the user to subclass either or
both of these models and supplement them with their own implementations.
You could use Abstract classes (e.g. ``BaseParent`` and ``BaseChild``)
for this, but then you would either need to:

1. Avoid putting the foreign key on ``BaseChild`` and tell the user they
   need to do it.
2. Put the foreign key on ``BaseChild``, but make ``Parent`` a concrete
   model that can't be swapped
3. Use swappable models, together with ``ForeignKeys`` that read the
   swappable settings.

This third approach is taken by Django to facilitate swapping of the
auth User model. Swapper extends this approach to apply to any model.

Getting Started
---------------

.. code:: bash

    pip install swapper

Usage
-----

Extending the above example, create abstract base classes and default
implementations:

.. code:: python

    # reusableapp/models.py
    from django.db import models
    from swapper import swappable_setting, get_model_name

    class BaseParent(models.Model):
        # minimal base implementation ...
        class Meta:
            abstract = True

    class Parent(BaseParent):
        # default (swappable) implementation ...
        class Meta:
           swappable = swappable_setting('reusableapp', 'Parent')

    class BaseChild(models.Model):
        parent = models.ForeignKey(get_model_name('reusableapp', 'Parent'))
        # minimal base implementation ...
        class Meta:
            abstract = True

    class Child(BaseChild):
        # default (swappable) implementation ...
        class Meta:
           swappable = swappable_setting('reusableapp', 'BaseChild')

Then the user can override one or both models in their own app:

.. code:: python

    # myapp/models.py
    from reusableapp.models import BaseParent
    class Parent(BaseParent):
        # custom implementation ...

The user then specifies the appropriate setting to trigger the swap:

.. code:: python

    # myproject/settings.py
    REUSABLEAPP_PARENT_MODEL = "myapp.Parent"

Note: Instead of importing concrete models directly, always use the
swapper: \`\`\`python # reusableapp/views.py

Might work, might not
=====================

from .models import Parent
==========================

from swapper import load\_model Parent = load\_model("reusableapp",
"Parent") Child = load\_model("reusableapp", "Parent")

def view(request, \*args, \*\*kwargs): qs = Parent.objects.all() # ...
