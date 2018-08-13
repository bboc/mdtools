init:
	pip install -r requirements.txt

test:
	nosetests

dev:
	python setup.py develop

docs:

	ifneq ("$(wildcard docs/img)","")
		rm -r docs/img
	endif
	cp -r docs-src/img docs/img
	CONFIG=docs-src/structure.yaml
	GLOSSARY=docs-src/en/glossary.yaml
	SECTIONINDEX=docs-src/en/section-index.yaml

	mdslides build-index-db $(CONFIG) $(SECTIONINDEX)
	mdslides build jekyll $(CONFIG) docs-src/en/src docs/ --glossary=$(GLOSSARY) --template=docs-src/en/website/_templates/index.md --index=$(SECTIONINDEX) --section-index-template=docs-src/en/website/_templates/pattern-index.md --introduction-template=docs-src/en/website/_templates/introduction.md
	cd docs;jekyll build