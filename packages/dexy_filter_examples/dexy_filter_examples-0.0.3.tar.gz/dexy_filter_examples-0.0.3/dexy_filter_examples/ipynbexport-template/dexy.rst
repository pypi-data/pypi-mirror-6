IPython Notebook Filter Examples
--------------------------------

{% from "dexy.jinja" import hl, ext with context -%}

The `ipynb` filter extracts information from an ipython notebook and returns it
in JSON format. It also creates additional documents for each cell based on the
type of cell. A list of these documents are included in the JSON.
