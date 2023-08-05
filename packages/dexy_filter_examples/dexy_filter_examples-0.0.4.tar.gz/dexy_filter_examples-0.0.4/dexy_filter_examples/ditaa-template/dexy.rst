ditaa Examples
--------------

{% from "dexy.jinja" import ext with context -%}

This filter runs http://ditaa.sourceforge.net/

Here is an example of some ascii art::

    {{ d['diagram.txt'] | indent(4) }}

Here is how to convert this to an image using `ditaa`::

    {{ d['dexy.yaml|idio|t']['ditaa'] | indent(4) }}

{% if ext == ".html" %}

Here is the generated image:

.. image:: diagram.png

{% endif -%}

You can pass command line args to modify the image::

    {{ d['dexy.yaml|idio|t']['args'] | indent(4) }}

{% if ext == ".html" %}

Here is the generated image:

.. image:: rounded.png

{% endif -%}
