Asciidoc Filter
---------------

{% from "dexy.jinja" import hl, ext with context -%}

The `asciidoc` filter takes asciidoc content, like this::

    {{ d['example.adoc'] | indent(4) }}

And converts it using the `asciidoc` command.
 
{% if ext == '.html' %}

.. raw:: html

    <iframe src="asciidoc/example.html" style="border: thin solid grey; width: 100%; height: 400px;">
    </iframe>

{% endif %}

