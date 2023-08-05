Julia Examples
--------------

{% from "dexy.jinja" import hl, ext with context -%}

The website for julia is `julialang <http://julialang.org>`__.

Here is some julia code:

{{ hl(d['math.jl'], "julia") }}

The `julia` filter runs code through the julia interpreter in batch mode::

    {{ d['dexy.yaml|idio|t']['julia'] | indent(4) }}

Here is the output, just what was printed to stdout::

    {{ d['math.jl|julia'] | indent(4) }}

THe `jlcon` filter runs code through the julia REPL. Here is how it's specified::

    {{ d['dexy.yaml|idio|t']['jlcon'] | indent(4) }}

Here is the output::

    {{ d['math.jl|jlcon'] | indent(4) }}

Julia code can be divided into sections before processing::

    {{ d['dexy.yaml|idio|t']['jlcon-sections'] | indent(4) }}

Here is just the first section::

    {{ d['math.jl|idio|jlcon']['math'] | indent(4) }}

