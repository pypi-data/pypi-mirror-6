Code
----

{% from 'dexy.jinja' import codes with context -%}

First, we assign variables:

{{ codes('script.py|idio', 'assign-variables') }}

Then, we multiply:

{{ codes('script.py|idio', 'multiply') }}

Output
------

The output is::

    {{ d['script.py|py'] | indent(4) }}

