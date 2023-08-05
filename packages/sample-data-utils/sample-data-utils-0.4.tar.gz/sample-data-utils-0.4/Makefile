VERSION=2.0.0
BUILDDIR='~build'

PYTHONPATH:=${PWD}

docs:
	mkdir -p ${BUILDDIR}/
	sphinx-build -aE docs ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif

mkbuilddir:
	mkdir -p ${BUILDDIR}

test:
	export PYTHONPATH=${PYTHONPATH}
	py.test -vv

coverage: mkbuilddir
	py.test --cov-report xml --cov-report html --junitxml=pytest.xml --cov-config=tests/.coveragerc -vv --cov sample_data_utils
ifdef BROWSE
	firefox ${BUILDDIR}/coverage/index.html
endif

ci:
	@pip install coverage
	$(MAKE) coverage

clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage coverage.xml pytest.xml .cache MANIFEST
	find . -name __pycache__ -prune | xargs rm -rf
	find . -name "*.py?" -prune | xargs rm -rf
	find . -name "*.orig" -prune | xargs rm -rf


.PHONY: docs
