# Makefile for pyword.

SETUP = python setup.py
MANIFEST = MANIFEST.in
EXCLUDE = .hgignore .hgtags $(MANIFEST)
FORMATS = sdist --formats=gztar,zip bdist --formats=wininst
RELEASE = upload

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build doc

all:		build

build:;		@ $(SETUP) $@

sdist:;		@ echo "exclude $(EXCLUDE)" > $(MANIFEST)
		@ $(SETUP) $@ --formats=gztar
		@ rm -f $(MANIFEST)

bdist:;		@ $(SETUP) $@ --formats=wininst

release:;	@ echo "exclude $(EXCLUDE)" > $(MANIFEST)
		@ $(SETUP) $(FORMATS) $(RELEASE)
		@ rm -f $(MANIFEST)

doc:;		@ $(SETUP) build_sphinx

tags:;		find . -name '*.py' | xargs etags

clean:;		rm -rf $(MANIFEST) build dist *.egg-info
