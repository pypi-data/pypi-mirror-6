IPython Notebook Filter Examples
--------------------------------

{% from "dexy.jinja" import hl, ext with context -%}

The `ipynb` filter extracts information from an ipython notebook and returns it
in JSON format. It also creates additional documents for each cell based on the
type of cell. A list of these documents are included in the JSON.

Here is an example::

    {{ ppjson(str(d['Trapezoid Rule.ipynb|ipynb'])) | indent(4) }}

We can iterate over the listed documents and display their contents:

{% for doc in d['Trapezoid Rule.ipynb|ipynb'].from_json()['documents'] %}
{{ doc }}

{% if d[doc].ext in [".png"] %}

.. image:: {{ d[doc].url_quoted_name() }}

{% else %}

::

    {{ d[doc] | indent(4) }}

{% endif %}

{% endfor -%}
