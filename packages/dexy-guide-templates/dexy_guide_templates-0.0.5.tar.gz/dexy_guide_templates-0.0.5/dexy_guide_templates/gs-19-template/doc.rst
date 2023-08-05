Code
----

First, we assign variables:

.. raw:: html

    {{ d['script.py|idio']['assign-variables'] | indent(4) }}

Then, we multiply:

.. raw:: html

    {{ d['script.py|idio']['multiply'] | indent(4) }}

Output
------

The output is::

    {{ d['script.py|py'] | indent(4) }}

