htmlsections Filter
-------------------

Here is some HTML split into sections::

    {{ d['sections.html'] | indent(4) }}

Here is another HTML document which includes some sections::

    {{ d['docs.html'] | indent(4) }}

After running dexy, the sections are included::

    {{ d['docs.html|jinja'] | indent(4) }}

Here is how we specify this::

    {{ d['dexy.yaml'] | indent(4) }}
