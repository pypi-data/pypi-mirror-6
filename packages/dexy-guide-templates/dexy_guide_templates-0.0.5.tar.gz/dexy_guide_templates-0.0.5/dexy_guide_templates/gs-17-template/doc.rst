Code
----

{% from 'rst.jinja' import rst_code with context -%}

First, we assign variables:

{{ rst_code('script.py|idio|t', 'assign-variables', number_lines=True) }}

Then, we multiply:

{{ rst_code('script.py|idio|t', 'multiply') }}

Output
------

The output is::

    {{ d['script.py|py'] | indent(4) }}

