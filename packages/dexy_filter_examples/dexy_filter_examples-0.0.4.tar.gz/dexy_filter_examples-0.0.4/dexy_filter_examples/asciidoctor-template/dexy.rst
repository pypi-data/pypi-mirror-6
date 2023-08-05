Asciidoc Filter
---------------

{% from "dexy.jinja" import hl, ext, codes, code with context -%}

The `asciidoc` filter takes asciidoc content, like this::

    {{ d['example1.adoc'] | indent(4) }}

And converts it using the `asciidoc` command::

    {{ d['dexy.yaml|idio|t']['default'] | indent(4) }}
 
{% if ext == '.html' %}

.. raw:: html

    <iframe src="asciidoctor/example1.html" style="border: thin solid grey; width: 100%; height: 400px;">
    </iframe>

{% endif %}

Custom `asciidoctor stylesheets <http://asciidoctor.org/docs/produce-custom-themes-using-asciidoctor-stylesheet-factory/>`__ can be specified::

    {{ d['dexy.yaml|idio|t']['custom-stylesheet'] | indent(4) }}

{% if ext == '.html' %}

.. raw:: html

    <iframe src="asciidoctor/example2.html" style="border: thin solid grey; width: 100%; height: 400px;">
    </iframe>

{% endif %}
