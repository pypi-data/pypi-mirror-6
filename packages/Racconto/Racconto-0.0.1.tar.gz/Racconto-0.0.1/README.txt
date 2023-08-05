Get a list of commands available
--------------------------------
python -m racconto --help

Generate site
-------------
python -m racconto --generate

Note about Pygments and syntax highlightning
--------------------------------------------
If you want syntax highlightning in your generated HTML files, use fenced
code blocks in your markdown content and install Pygments (pip install pygments).

Run tests
---------
Install project dependencies in a virtualenv then run:
python -m unittest discover --pattern=test_*.py
