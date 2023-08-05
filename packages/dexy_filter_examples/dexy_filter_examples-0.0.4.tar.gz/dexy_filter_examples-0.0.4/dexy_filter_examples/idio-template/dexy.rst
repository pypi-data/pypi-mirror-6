Idio Example
============

The idio filter splits source code according to comments found in the code.
Many different comment formats are supported, please let us know if you need
additional formats supported for your programming language.

Shortcut Quoted Form
--------------------

You can write idio comments by using three comment characters and putting the section name in quotes, like this::

    {{ d['example.py'] | indent(4) }}

The resulting section names are:

    {{ ", ".join(d['example.py|idio'].keys()) | assert_contains("foo") | assert_contains("bar") }}

For languages which support `//` as a comment char, just use three slashes instead of two::

    {{ d['example.c'] | indent(4) }}

Here are the section names::

    {{ ", ".join(d['example.c|idio'].keys()) | assert_contains("include") | assert_contains("main") }}

Here is the script output::

    {{ d['example.c|c'] | indent(4) }}

(A `/* */` multiline-style comment is also supported, see the next section.)

The `;` comment character is supported for Clojure::

    {{ d['example.clj'] | indent(4) }}

Here is the output from running the full clojure script::

    {{ d['example.clj|clj'] | indent(4) }}

Here is the REPL output from just the `foo` section of the clojure script::

    {{ d['example.clj|idio|cljint']['foo'] | indent(4) | assert_contains("hello") | assert_does_not_contain("world") }}

The `%` comment character is supported, for LaTeX::

    {{ d['example.tex'] | indent(4) }}

Here are the section names::

    {{ ", ".join(d['example.tex|idio'].keys()) | assert_contains("foo") | assert_contains("bar") }}


Long Form
---------

The original idio syntax uses the `@export` keyword followed by a name, which need not be in quotes. This format is still supported::

    {{ d['original-syntax.py'] | indent(4) }}

The resulting section names are::

    {{ ", ".join(d['original-syntax.py|idio'].keys()) | assert_contains("foo") | assert_contains("bar") }}

To use a multi-line style comment, use three initial asterisks and the `@export` keyword::

    {{ d['multiple-example.c'] | indent(4) }}

Here are the section names::

    {{ ", ".join(d['multiple-example.c|idio'].keys()) | assert_contains("include") | assert_contains("main") }}

Here is the script output::

    {{ d['multiple-example.c|c'] | indent(4) }}

HTML style comments are also supported::

    {{ d['example.html'] | indent(4) }}

Here are the section names::

    {{ ", ".join(d['example.html|idio'].keys()) | assert_contains("foo") | assert_contains("bar") }}
