ROOT=docs-src
CONFIG=$(ROOT)/en/structure-new.yaml
GLOSSARY=$(ROOT)/en/glossary.yaml

TMPFOLDER=tmp

LOC=$(ROOT)/en/localization.po
PRJ=$(ROOT)/config/project.yaml
MKTPL=mdslides template

# get language specific parameters
include $(ROOT)/config/make-conf

define update-make-conf
# update the make conf file from translations
$(MKTPL) $(ROOT)/templates/make-conf $(ROOT)/config/make-conf $(LOC) $(PRJ)
endef

init:
	pip install -r requirements.txt

test:
	nosetests

dev:
	python setup.py develop

revealjs:
	$(update-make-conf)

	$(MKTPL) $(ROOT)/templates/revealjs-template.html $(TMPFOLDER)/revealjs-template.html $(LOC) $(PRJ)

	mdslides compile $(CONFIG) $(ROOT)/en/src $(TMPFOLDER) --chapter-title=text --glossary=$(GLOSSARY) --section-prefix="$(SECTIONPREFIX)"
	mdslides build revealjs $(CONFIG) $(TMPFOLDER) docs/slides.html --template=$(TMPFOLDER)/revealjs-template.html  --glossary=$(GLOSSARY) --glossary-items=8

site:
	# build jekyll site
	$(update-make-conf)

	# prepare templates
	$(MKTPL) $(ROOT)/templates/docs/_layouts/default.html docs/_layouts/default.html $(LOC) $(PRJ)
	$(MKTPL) $(ROOT)/templates/docs/_config.yml docs/_config.yml $(LOC) $(PRJ)
	#$(MKTPL) $(ROOT)/templates/docs/CNAME docs/CNAME $(LOC) $(PRJ)
	$(MKTPL) $(ROOT)/en/website/_includes/footer.html docs/_includes/footer.html $(LOC) $(PRJ)
	cp $(ROOT)/en/website/_includes/header.html docs/_includes/header.html


ifneq ("$(wildcard docs/img)","")
	rm -r docs/img
endif
	cp -r $(ROOT)/img docs/img

	mdslides build jekyll $(CONFIG) $(ROOT)/en/src docs/ --glossary=$(GLOSSARY) --template=$(ROOT)/en/website/_templates/index.md --section-index-template=$(ROOT)/en/website/_templates/pattern-index.md --introduction-template=$(ROOT)/en/website/_templates/introduction.md
	cd docs;jekyll build