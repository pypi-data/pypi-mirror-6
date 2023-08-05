
.SUFFIXES :
.PRECIOUS :
.PHONY : FORCE
.DELETE_ON_ERROR:

SHELL:=/bin/bash -o pipefail
SELF:=$(firstword $(MAKEFILE_LIST))

UTA_DB_URL=postgresql://uta_public:uta_public@uta.invitae.com/uta
#UTA_DB_URL=sqlite:///tmp/uta-0.0.5.db
#UTA_DB_URL=postgresql://localhost/uta

############################################################################
#= BASIC USAGE
default: help

#=> help -- display this help message
help: config
	@sbin/extract-makefile-documentation "${SELF}"

config:
	@echo CONFIGURATION
	@echo "  UTA_DB_URL=${UTA_DB_URL}"


############################################################################
#= SETUP, INSTALLATION, PACKAGING

#=> ve -- create a virtualenv
VE_DIR:=ve
VE_MAJOR:=1
VE_MINOR:=10
VE_PY_DIR:=virtualenv-${VE_MAJOR}.${VE_MINOR}
VE_PY:=${VE_PY_DIR}/virtualenv.py
${VE_PY}:
	curl -sO  https://pypi.python.org/packages/source/v/virtualenv/virtualenv-${VE_MAJOR}.${VE_MINOR}.tar.gz
	tar -xvzf virtualenv-${VE_MAJOR}.${VE_MINOR}.tar.gz
	rm -f virtualenv-${VE_MAJOR}.${VE_MINOR}.tar.gz
${VE_DIR}: ${VE_PY} 
	${SYSTEM_PYTHON} $< ${VE_DIR} 2>&1 | tee "$@.err"
	/bin/mv "$@.err" "$@"

# => setup
setup: requirements.txt build
	pip install -r $<

#=> develop, build_sphinx, sdist, upload_sphinx
bdist bdist_egg build build_sphinx develop install sdist upload_sphinx upload_docs: %:
	python setup.py $*

# sphinx docs needs to be able to import packages
build_sphinx: develop

#=> upload
upload:
	python setup.py bdist_egg sdist upload


############################################################################
#= TESTING

#=> test -- run tests
test-setup: install

#=> test, test-with-coverage -- per-commit test target for CI
test test-with-coverage: test-setup
	python setup.py nosetests --with-xunit --with-coverage --cover-erase --cover-package=hgvs --cover-html 

#=> ci-test-nightly -- per-commit test target for CI
ci-test jenkins:
	make ve \
	&& source ve/bin/activate \
	&& make install \
	&& make test \
	&& make docs


############################################################################
#= UTILITY TARGETS

#=> docs -- make sphinx docs
docs: build_sphinx

#=> lint -- run lint, flake, etc
# TBD


############################################################################
#= CLEANUP
.PHONY: clean cleaner cleanest pristine
#=> clean: clean up editor backups, etc.
clean:
	find . -name \*~ -print0 | xargs -0r /bin/rm
#=> cleaner: above, and remove generated files
cleaner: clean
	find . -name \*.pyc -print0 | xargs -0r /bin/rm -f
	/bin/rm -fr build bdist dist sdist ve virtualenv*
	-make -C doc clean
#=> cleanest: above, and remove the virtualenv, .orig, and .bak files
cleanest: cleaner
	find . \( -name \*.orig -o -name \*.bak \) -print0 | xargs -0r /bin/rm -v
	/bin/rm -fr distribute-* *.egg *.egg-info *.tar.gz nosetests.xml
#=> pristine: above, and delete anything unknown to mercurial
pristine: cleanest
	hg st -un0 | xargs -0r echo /bin/rm -fv

## <LICENSE>
## Copyright 2014 HGVS Contributors (https://bitbucket.org/invitae/hgvs)
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##     http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## </LICENSE>
