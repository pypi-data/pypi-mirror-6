Bash Examples
-------------

Here is a simple bash script::

    {{ d['script.sh'] | indent(4) }}

The bash filter runs scripts in bash and returns the output::

    {{ d['dexy.yaml|idio']['bash'] | indent(4) }}

Here is the output::

    {{ d['script.sh|bash'] | indent(4) }}

The sh filter runs scripts in sh (dash) and returns the output::

    {{ d['dexy.yaml|idio']['sh'] | indent(4) }}

Here is the output::

    {{ d['script.sh|sh'] | indent(4) }}

The shint filter runs scripts in a bash REPL, so you can see both input and output::

    {{ d['dexy.yaml|idio']['shint'] | indent(4) }}

Here is the output::

    {{ d['script.sh|shint'] | indent(4) }}

Normally, bash scripts run in a temporary working directory created and
populated especially for the filter being run, but if you want to run a bash
script which operates on your actual project directory, you can use the use-wd
setting like this (this works on any of the bash-related filters)::

    {{ d['dexy.yaml|idio']['whereami'] | indent(4) }}

    {{ d['whereami.sh|shint'] | indent(4) }}

The default behavior of running in a working directory is intended to allow you
to work with dependencies which have already been processed by dexy, and it
also is intended to protect your working directory from side effects of running
your bash script.
