=============================
Analog - Log Analysis Utility
=============================

Analog is a weblog analysis utility that provides these metrics:

* Number for requests.
* Response request method (HTTP verb) distribution.
* Response status code distribution.
* Requests per path.
* Response time statistics (mean, median).
* Response upstream time statistics (mean, median).
* Response body size in bytes statistics (mean, median).
* Per path request method (HTTP verb) distribution.
* Per path response status code distribution.
* Per path response time statistics (mean, median).
* Per path response upstream time statistics (mean, median).
* Per path response body size in bytes statistics (mean, median).

Documentation is on `analog.readthedocs.org <http://analog.readthedocs.org/>`_,
code and issues are on `bitbucket.org/fabianbuechler/analog
<https://bitbucket.org/fabianbuechler/analog>`_ and the package can be installed
from PyPI at `pypi.python.org/pypi/analog
<https://pypi.python.org/pypi/analog>`_.


Changelog
=========

0.1.5 - 2014-01-27
------------------

* Replace numpy with backport of statistics for mean and median calculation.

0.1.4 - 2014-01-27
------------------

* Move fallback for verbs, status_codes and paths configuration to ``analyzer``.
  Also use the fallbacks in ``analog.analyzer.Analyzer.__init__`` and
  ``analog.analyzer.analyze``.

0.1.3 - 2014-01-27
------------------

* Fix API-docs building on readthedocs.

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


