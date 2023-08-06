#-*- coding: utf-8 -*-
#:Progetto:  SoL
#:Creato:    sab 08 nov 2008 21:16:39 CET
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

export TOPDIR := $(CURDIR)
PYTHON := $(BINDIR)python
SOLSRC := $(TOPDIR)/src/sol
MANIFEST := manifest.json
MEDSRC := $(shell $(PYTHON) -c "from pkg_resources import resource_filename as rfn;print(rfn('metapensiero.extjs.desktop',''))")
PACKED_CSS := $(SOLSRC)/static/all-styles.css
PACKED_JS := $(SOLSRC)/static/all-classes.js
SOLADMIN := $(BINDIR)soladmin
MINIFIER := $(BINDIR)minify_js_scripts \
		--output-js $(PACKED_JS) \
		--output-css $(PACKED_CSS) \
		--prefix-map /static=$(SOLSRC)/static \
		--prefix-map /desktop=$(MEDSRC)/assets \
		--prefix-map SoL=$(SOLSRC)/static/app \
		--prefix-map MP=$(MEDSRC)/assets/js \
		--prefix-map Ext=$(MEDSRC)/assets/extjs/src \
		--extjs-auto-deps \
		--extjs-core-bundle $(MEDSRC)/assets/extjs/ext-dev.js \
		$(MANIFEST)
YUICOMPRESSOR := $(BINDIR)yuicompressor
ALEMBIC = $(BINDIR)alembic -n app:main -c development.ini
LANGS = it en
SOL_INIT = $(SOLSRC)/__init__.py

.PHONY: html
html: $(foreach lang,$(LANGS),html-$(lang))
	@rm -rf $(SOLSRC)/static/manual && ( \
	  cp -a docs/_build/html $(SOLSRC)/static/manual; \
	  for lang in $(LANGS); do \
	    cp -a docs/_build/$$lang/html $(SOLSRC)/static/manual/$$lang; \
	    [ -f $(SOLSRC)/static/manual/$$lang/_static/translations.js ] && \
	      mv $(SOLSRC)/static/manual/$$lang/_static/translations.js $(SOLSRC)/static/manual/_static/translations-$$lang.js; \
	    rm -rf $(SOLSRC)/static/manual/$$lang/_static; \
	    for html in $(SOLSRC)/static/manual/$$lang/*.html; do \
	      sed -i "s,_static/translations\.js,_static/translations-$$lang.js,g" $$html; \
	      sed -i 's,"_static/,"../_static/,g' $$html; \
	    done; \
	  done; \
	)

html-%: html-dev
	$(MAKE) -C docs/$(@:html-%=%) -f ../Makefile html LANGDIR=/$(@:html-%=%)

.PHONY: html-dev
html-dev:
	$(MAKE) -C docs html

.PHONY: minimize
minimize: $(SOLSRC)/static/ext.js
	$(MINIFIER)

$(SOLSRC)/static/ext.js: $(MEDSRC)/assets/extjs/ext-dev.js
	$(YUICOMPRESSOR) $< -o $@

requirements/versions.cfg: requirements/base.txt $(VERSION_TXT)
	@echo "[versions]" > $@
	@sed 's/==/ = /' $< >> $@
	@echo 'SoL = $(VERSION)' >> $@

.PHONY: clean
clean:
	$(MAKE) -C docs clean
	rm -rf build $(SOLSRC)/static/manual
	rm -f $(PACKED_CSS) $(PACKED_JS)
	-@find docs src -name '*~' -print0 | xargs -r0 rm

.PHONY: distclean
distclean: clean
	rm -f development.db

development.db:
	$(SOLADMIN) initialize-db development.ini
	$(SOLADMIN) restore development.ini

.PHONY: generate-db-migration
generate-db-migration:
	read -p "Enter migration description: " MDESC && \
	  $(ALEMBIC) revision --autogenerate -m "$$MDESC"

.PHONY: upgrade-db
upgrade-db:
	$(SOLADMIN) upgrade-db development.ini

.PHONY: serve
serve: development.db
	pserve development.ini

.PHONY: test
test:
	$(PYTHON) setup.py nosetests

include Makefile.i18n
include Makefile.release
