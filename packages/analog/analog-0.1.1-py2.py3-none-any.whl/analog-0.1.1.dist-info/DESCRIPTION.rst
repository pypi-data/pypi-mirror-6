=============================
Analog - Log Analysis Utility
=============================

Analog is a weblog analysis utility that provides these metrics:

* Number for requests.
* Response request method (HTTP verb) distribution.
* Response status code distribution.
* Requests per path.
* Response time statistics (mean, median, 90th, 75th and 25th percentiles).
* Response upstream time statistics (as above).
* Response body size in bytes statistics (as above).
* Per path request method (HTTP verb) distribution.
* Per path response status code distribution.
* Per path response time statistics (as above).
* Per path response upstream time statistics (as above).
* Per path response body size in bytes statistics (as above).

Documentation is on `analog.readthedocs.org <http://analog.readthedocs.org/>`_,
code and issues are on `bitbucket.org/fabianbuechler/analog
<https://bitbucket.org/fabianbuechler/analog>`_ and the package can be installed
from PyPI at `pypi.python.org/pypi/analog
<https://pypi.python.org/pypi/analog>`_.


Changelog
=========

0.1.1 - 2014-01-26
------------------

* Add numpy to ``requirements.txt`` since installation via ``setup.py install``
  does not work.

* Strip VERSION when reading it in setup.py.

0.1.0 - 2014-01-26
------------------

* Start documentation: quickstart and CLI usage plus API documentation.

* Add renderers for CSV and TSV output. Use --output [csv|tsv].
  Unified codebase for all tabular renderers.

* Add renderer for tabular output. Use --output [grid|table].

* Also analyze HTTP verbs distribution for overall report.

* Remove timezone aware datetime handling for the moment.

* Introduce Report.add method to not expose Report externals to Analyzer.

* Install pytz on Python <= 3.2 for UTC object. Else use datetime.timezone.

* Add tox environment for py2.7 and py3.3 testing.

* Initial implementation of log analyzer and report object.

* Initial package structure, docs, requirements, test scripts.


