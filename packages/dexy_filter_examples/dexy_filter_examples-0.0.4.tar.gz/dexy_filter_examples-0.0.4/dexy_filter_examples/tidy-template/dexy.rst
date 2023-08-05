HTML Tidy
---------

Here's an example of some invalid HTML::

    {{ d['invalid.html'] | indent(4) }}

The `tidyerrors` filter will report on what the errors are::

    {{ d['dexy.yaml|idio']['tidyerrors'] | indent(4) }}

    {{ d['invalid.html|tidyerrors'] | indent(4) }}

Here's some valid HTML::

    {{ d['dexy.yaml|idio']['tidycheck'] | indent(4) }}

    {{ d['valid.html'] | indent(4) }}

The `tidycheck` filter will let the valid HTML pass through unchanged::

    {{ d['valid.html|tidycheck'] | indent(4) }}

If we were to run the `tidycheck` filter on invalid HTML, it would raise an
exception.

The `tidy` filter will apply tidy to valid HTML::

    {{ d['dexy.yaml|idio']['tidy'] | indent(4) }}

    {{ d['valid.html|tidy'] | indent(4) }}

If we were to run the `tidy` filter on invalid HTML, it would raise an
exception.
