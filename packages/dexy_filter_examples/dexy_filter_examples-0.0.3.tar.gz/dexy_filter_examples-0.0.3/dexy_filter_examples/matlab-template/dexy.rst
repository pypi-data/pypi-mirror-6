Matlab Examples
---------------

{% from "dexy.jinja" import ext with context -%}

Here is some matlab code::

    {{ d['example.m'] | indent(4) }}

The `matlabint` filter runs code through the matlab interpreter, here is how to specify this::

    {{ d['dexy.yaml|idio|t']['matlab'] | indent(4) }}

Here is the output::

    {{ d['example.m|matlabint'] | indent(4) }}

Code can also be run in sections by putting it through the `idio` filter first::

    {{ d['dexy.yaml|idio|t']['matlab-sections'] | indent(4) }}

The `add-new-files` setting is required if your script generates additional
files (such as plots) which you wish to reference in documents.

Here is just the section which produces a plot::

    {{ d['example.m|idio|matlabint']['image'] | indent(4) }}

{% if ext == ".html" %}

Here is the generated plot:

.. image:: matlab-plot.png

{% endif -%}

Matlab files which reference simulink models can also be processed. The `.slx`
file needs to be specified as an input::

    {{ d['dexy.yaml|idio|t']['simulink'] | indent(4) }}

You can set the `timeout` parameter (in seconds) if your script will take more
than 10 seconds to run.

Here is the matlab file which calls the model::

    {{ d['simexample.m'] | indent(4) }}

Here is the output when run::

    {{ d['simexample.m|matlabint'] | indent(4) }}

{% if ext == ".html" %}

Here is the simulation diagram:

.. image:: simulink-window.png

Here is the generated plot:

.. image:: matlab-sim-plot.png

{% endif -%}
