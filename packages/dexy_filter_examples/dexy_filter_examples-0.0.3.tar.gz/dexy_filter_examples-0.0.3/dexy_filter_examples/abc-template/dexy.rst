ABC Filter
----------

{% from "dexy.jinja" import ext with context -%}

`ABC <http://abc.sourceforge.net/>`__ is a music notation which looks like this::

    {{ d['jingle.abc'] | indent(4) }}

The abc filter converts this to one of the available output formats, using the
`abcm2ps` utility which must be installed on your system. By default it will
convert to SVG::


    {{ d['dexy.yaml|idio|t']['jingle'] | indent(4) }}

{% if ext == ".html" %}

.. image:: jingle.svg

{% endif -%}

Here is some of the SVG generated::

    {{ d['jingle.abc|abc'] | head(10) | indent(4) }}

To get EPS or another type of output, set the desired file extension::

    {{ d['dexy.yaml|idio|t']['jingle-eps'] | indent(4) }}

Here is some of the EPS generated::

    {{ d['jingle.abc|abc|-'] | head(10) | indent(4) }}

You can also run the dexy `eps2pdf` filter to generate a PDF. In this case you
don't need to specify any custom file extension because `eps2pdf` only accepts
`.eps` files as inputs. In this example, we also set some custom command line
arguments which get passed to `abcm2ps`::

    {{ d['dexy.yaml|idio|t']['jingle-eps-to-pdf'] | indent(4) }}

{% if ext == ".html" %}
`Here <jingle.pdf>`__ is the resulting PDF.
{% endif %}

To generate HTML you can use the shortcut `h` filter which forces the previous
filter to output HTML::

    {{ d['dexy.yaml|idio|t']['jingle-html'] | indent(4) }}

The HTML output format wraps SVG output in a self-contained HTML page.
