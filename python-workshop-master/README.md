Setup and Activate Python Virtual Environment
=============================================

Setup Python virtual environment (https://docs.python.org/3/tutorial/venv.html):

```
# On MacOS and Linux
python3 -m venv venv

# On Windows
python -m venv venv
```

For details about Python virtual enviroments read https://realpython.com/python-virtual-environments-a-primer/

Activate virtual environment (you need to do this every time you start a new terminal):

```
# On MacOS and Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate.bat
```

Install Example Application in Development Mode
===============================================

Install mk-log-analyzer (this example application) in development mode:

```
python setup.py develop
```

The above command will install all dependencies required for running the application (listed
in _setup.py_; see `install_requires` argument for `setuptools.setup`) and sets the virtual
environment to use code for `log_analyzer` Python package from current directory because `packages`
argument of `setuptools.setup` defines the _mk-log-analyzer_ package to include Python modules from
package called `log_analyzer`.

For info about packages and modules read https://realpython.com/python-modules-packages/

Try The Application
===================

The example logs (input files) are in *example_logs* directory.

```
python -m log_analyzer stats example_logs/example1.log
python -m log_analyzer convert example_logs/example1.log -o example1.jsonlog
python -m log_analyzer stats example1.jsonlog
python -m log_analyzer convert example_logs/example1.log --extract-containers
python -m log_analyzer convert example1.jsonlog --extract-containers
```


Install Used Tools
==================

```
pip install -r requirements/tools.txt
```

Run Static Analyzers
====================

```
prospector
```

Prospector is a tool to analyse Python code and output information about errors, potential
problems, convention violations and complexity.

See https://prospector.readthedocs.io/en/master/

Run Tests
=========

Because this is an example, unit tests have been implemented using Python's unittest module
(https://docs.python.org/3/library/unittest.html) and with PyTest (https://docs.pytest.org/en/latest/).

Run only the tests implented with Python's unittest module:

```
python -m unittest -v
```

Run all tests (both written with unittest module and PyTest):

```
pytest -vv
```

To run PyTest and record coverage run

```
pytest -vv --cov=log_analyzer
```

The above command shows coverage summary. To get more detailed report, run

```
coverage html
```

The command creates HTML report into _coverage_report_ directory; open index.html with your browser.


Update Used Tools
=================

Install pip-tools (https://github.com/jazzband/pip-tools)

```
pip install pip-tools
```


Update tools

```
pip-compile --upgrade --output-file requirements/tools.txt requirements/tools.in
```

Note that if there was updates, the _requirements/tools.txt_ tracked by git is updated, i.e. you
would commit the changes to that files (after testing that the new versions work with your code).
