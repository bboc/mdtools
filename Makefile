# #### the first part of the makefile handles building documentation #########

TMP=tmp
PROJECT=docs-src/config/project.yaml

# get language specific parameters
include docs-src/config/local-conf

site:
	# build jekyll site
	mdbuild jekyll $(PROJECT) -vv
	mdbuild all-in-one-jekyll-page $(PROJECT) -vv
	cd docs;jekyll build

rebuild-site:
	mdbuild jekyll $(PROJECT) -vv
	mdbuild all-in-one-jekyll-page $(PROJECT) -vv

serve-site:
	open http://127.0.0.1:4000/
	# serve jekyll site
	cd docs;jekyll serve
	//cd docs;jekyll serve --baseurl=
	# release the port if something went wrong:
	# ps aux |grep jekyll |awk '{print $2}' | xargs kill -9

debug:
	# build with debug output (for quickly testing changes to structure.yaml or project.yaml)
	mdbuild all-in-one-jekyll-page $(PROJECT) -vvvv

epub:
	# render an ebook as epub
	echo $(TARGETFILE)
	mdbuild epub $(PROJECT) -vv
	cd $(TMP); pandoc epub-compiled.md -f markdown -t epub3 --toc --toc-depth=3 -s -o ../$(TARGETFILE).epub

docx:
	# render an ebook as epub
	echo $(TARGETFILE)
	mdbuild epub $(PROJECT) -vv
	cd $(TMP); pandoc epub-compiled.md -f markdown -t docx --toc --toc-depth=3 -s -o ../$(TARGETFILE).docx


ebook:
	# render an ebook as pdf (via LaTEX)
	mdbuild ebook $(PROJECT) -vv

	cd $(TMP); multimarkdown --to=latex --output=ebook-compiled.tex ebook-compiled.md
	cd $(TMP); latexmk -pdf -xelatex -silent ebook.tex 

	cd $(TMP); mv ebook.pdf ../$(TARGETFILE).pdf
	
	# clean up
	cd $(TMP); latexmk -C

deckset:
	mdbuild deckset $(PROJECT) -vv

clean:
	# clean all generated content
	-rm -r docs/img
	-rm -r docs/_site
	-rm docs/*.md
	# take no risk here!
	-rm -r tmp

setup:
	# prepare temp folders and jekyll site
	echo "this might produce error output if folders already exist"
	-mkdir -p $(TMP)
	-mkdir docs/_site

	# copy images to temp folder
ifneq ("$(wildcard $(TMP)/img)","")
	# take no risk here!
	rm -r $(TMP)/img
endif
	cp -r docs-src/img $(TMP)/img

	# clean up and copy images do to docs folder
ifneq ("$(wildcard docs/img)","")
	rm -r docs/img
endif
	cp -r docs-src/img docs/img


# #####Commands for development of mdtools ######################

init:
	pip install -r requirements.txt
	python setup.py develop

test:
	nosetests

dev:
	python setup.py develop

