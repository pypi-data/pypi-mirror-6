Code
----

First, we assign variables:

.. code:: python
   :number-lines: 1

    {{ d['script.py|idio|t']['assign-variables'] | indent(4) }}

Then, we multiply:

.. code:: python

    {{ d['script.py|idio|t']['multiply'] | indent(4) }}

Output
------

The output is::

    {{ d['script.py|py'] | indent(4) }}

