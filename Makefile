#
#
#
PACKAGE:=
VERSION:=$(shell git describe --dirty)

all: lint # test

# Yes, this is ugly, yes make is weird.  For more "Make is weird", see
#   https://en.wikipedia.org/wiki/Make_(software)#cite_ref-esr_46-1
null:=
space:=$(null) #
comma:=,

BUILD_DEPS+=flake8
BUILD_DEPS+=python3-coverage
BUILD_DEPS+=python3-jsonschema
BUILD_DEPS+=python3-pytest
BUILD_DEPS+=python3-pytest-cov
BUILD_DEPS+=shellcheck
BUILD_DEPS+=yamllint
BUILD_DEPS+=yq

# Not available in current github actions ubuntu-latest
#BUILD_DEPS+=markdownlint

# These could get shellcheck run against them
SHELLSCRIPTS+=

# These get checked for consistent sort order
YAMLSORTED+=.github/workflows/ci.yml
YAMLSORTED+=.github/workflows/build.yml

EXCLUDE_LINT_PYTHON+=.venv/

.PHONY: dpkg
dpkg:
	rm -f debian/changelog
	dch --create --empty --package $(PACKAGE) -v ${VERSION}-0 --no-auto-nmu local package Auto Build
	dpkg-buildpackage -rfakeroot -us -uc
	mv ../*.deb ./

.PHONY: build-deps
build-deps:
	sudo apt-get -y install $(BUILD_DEPS)

# Run the lint steps in the order of fastest to slowest, so we can fail fast
.PHONY: lint
lint: lint.yaml lint.schema lint.python # lint.shell lint.markdown

.PHONY: test
test: test.python

.PHONY: lint.yaml
lint.yaml:
	yamllint --strict .
	scripts/yamlchecksorted.py $(YAMLSORTED)

.PHONY: lint.schema
lint.schema:
	#yq . .github/workflows/ci.yml | \
	#	jsonschema https://www.schemastore.org/github-workflow.json -o pretty
	#yq . .github/workflows/build.yml | \
	#	jsonschema https://www.schemastore.org/github-workflow.json -o pretty

.PHONY: lint.shell
lint.shell:
	shellcheck $(SHELLSCRIPTS)

.PHONY: lint.python
lint.python:
	flake8 --extend-exclude=$(subst $(space),$(comma),$(strip $(EXCLUDE_LINT_PYTHON)))

.PHONY: lint.markdown
lint.markdown:
	mdl .

.PHONY: test.python
test.python:
	pytest-3 \
	    --cov-report=term-missing \
	    --cov-report=html \
	    --cov-fail-under=50 \
	    --cov=.
