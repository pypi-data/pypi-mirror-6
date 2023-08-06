CURL ?= curl
ENVDIR ?= $(CURDIR)/env
FIND ?= find
FLAKE8 = $(ENVDIR)/bin/flake8
MKDIR ?= mkdir -p
NOSE = $(ENVDIR)/bin/nosetests
PIP = $(ENVDIR)/bin/pip
PYLINT = $(ENVDIR)/bin/pylint
PYTHON = $(ENVDIR)/bin/python
STATEDIR = $(ENVDIR)/.state
TAR ?= tar
TOUCH ?= touch
VIRTUALENV ?= pyvenv
# VIRTUALENV ?= virtualenv --quiet --prompt='{fluent-test}' --no-setuptools --no-pip

PIP_URL ?= https://raw.github.com/pypa/pip/master/contrib/get-pip.py
SETUPTOOLS_URL ?= https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

REQUIREMENTS := $(STATEDIR)/requirements-installed $(STATEDIR)/test-requirements-installed $(STATEDIR)/tools-installed


.PHONY: environment

environment: $(ENVDIR) $(REQUIREMENTS)

$(STATEDIR)/requirements-installed: $(STATEDIR) requirements.txt
	$(PIP) install -qr requirements.txt
	@ $(TOUCH) "$@"

$(STATEDIR)/test-requirements-installed: $(STATEDIR) test-requirements.txt
	$(PIP) install -qr test-requirements.txt
	@ $(TOUCH) "$@"

$(STATEDIR)/tools-installed: $(STATEDIR) tools.txt
	$(PIP) install -qr tools.txt
	@ $(TOUCH) "$@"

$(ENVDIR):
	$(VIRTUALENV) $(ENVDIR)
	@ $(MKDIR) $(ENVDIR)/tmp
	@ cd $(ENVDIR)/tmp && $(CURL) -Ls -o- $(SETUPTOOLS_URL) | $(PYTHON)
	@ cd $(ENVDIR)/tmp && $(CURL) -Ls -o- $(PIP_URL) | $(PYTHON)
	@ $(RM) -r $(ENVDIR)/tmp
	@ $(MKDIR) $(STATEDIR)

$(STATEDIR): $(ENVDIR)


.PHONY: test lint
test: environment
	$(NOSE)

lint: environment
	$(FLAKE8) fluenttest tests
	- $(PYLINT) --rcfile=pylintrc fluenttest
	- $(PYLINT) --rcfile=pylintrc --disable=C,R,broad-except tests


.PHONY: clean mostly-clean dist-clean maintainer-clean

clean:
	- $(FIND) . -name '*.pyc' -delete
	- $(FIND) . -name '__pycache__' -delete
	- $(RM) .coverage

mostly-clean: clean
	- $(FIND) . -name '__pycache__' -delete
	- $(RM) -r build
	- $(RM) -r *.egg
	- $(RM) -r *.egg-info

dist-clean: mostly-clean
	- $(RM) -r dist

maintainer-clean: dist-clean
	- $(RM) -r $(ENVDIR)


.PHONY: sdist

sdist: environment
	$(PYTHON) setup.py sdist


.PHONY: docs

docs: environment
	$(PYTHON) setup.py build_sphinx
	@ test -d dist || $(MKDIR) dist
	cd build/doc/html && $(TAR) --create --gzip --file ../../../dist/Fluent-Test-docs.tar.gz .
