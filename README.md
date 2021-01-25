# mdtools

mdtools is a set of commandline scripts for creating electronic publications (books and slide-decks) in various output formats from a single source of (multi-)markdown files.

Publications created in mdtools are simple to tranlsate into other languages, as most translation platforms can handle all the formats used (markdown, html and po-files). 

The [S3 Practical Guide](http://patterns.sociocracy30.org/) is built with mdtools as Github page, pdf and ePub in several languages, and uses most of the advanced features mdtools provides: glossaries, summaries, tags, and auto-genarated indexes, see the project's [Github repository](https://github.com/S3-working-group/s3-practical-guide). 

You can find an introduction and documentation to mdtools in the example project, which is also the source of the [Github page for this repository](https://bboc.github.io/mdtools/). 

The simplest way for getting started with your own project is to copy the example project and play around with it.


## mdbuild

A powerful set of tools for rendering Github pages, and ebooks (pdf, ePub, Kindle format) from the same set of (Multi-)Markdown files. This makes it s

The structure of the book is defined in a yaml file, so that it is very simple to move around sections, chapters or parts, and a tag system allows for including or excluding files in different formats, and several other nifty features. 

## Image Update 

Update image references in MultiMarkdown files (while preserving Deckset formatting). This is helpful when maintaining a large set of illustrations used in a large number of markdown file, because it allows for changing the folder structure of the illustrations without having to worry about updating all the references. 

Usage: see `mdimg -h`


## mddiff

Output diff between two Markdown files as Critic Markup

Usage: see `mddiff -h`

## mdslides

**Warning: in version 2.0, mdslides is not working, support for slide decks will come back in a later version.**

Build slide decks from repositories of Markdown files for use in [Deckset](http://decksetapp.com), [reveal.js](http://lab.hakim.se/reveal-js) and Wordpress. This helps with reuse of slides and evolution of large decks.


## Installation

Starting with version 2.0, mdtools is developed and tested in Python 3 only (Python 3.9.1 currently).

### Setup

It's a good idea to install _mdtools_ in a [virtual environment](
https://docs.python.org/3/library/venv.html).

Clone the project (alternatively download and unzip the files):
    
    $ https://github.com/bboc/mdtools.git mdtools
    
Install dependencies and set up the commandline scripts:

    $ make init


### Dependencies

Most output formats require additional software:

- ePub: requires [Pandoc](https://pandoc.org/)
- pdf: requires [Multimarkdown](https://fletcherpenney.net/multimarkdown/), latexmk and texlive-xetex
- a Jekyll webpage would require a local [Jekyll](https://jekyllrb.com/) installations for testing changes to templates and CSS. For Github-pages, a local installation is not required, but often helpful.

#### MacOS

**Python 3.9**, **Pandoc** and **Multimarkdown** can be installed via a package manager, e.g. [Homebrew](https://brew.sh/) or [MacPorts](https://www.macports.org/). 

The simplest way to obtain **latexmk** and **texlive-xetex8* is the [MacTex-Distribution](https://www.tug.org/mactex/)

Instructions for installing Jekyll are available in the [Jekyll documentation](https://jekyllrb.com/docs/installation/macos/).  

#### Linux

Install the required dependencies via the package manager:

    $ sudo apt install latexmk texlive-xetex fonts-open-sans pandoc multimarkdown

On Linux, it might be necessary to Multimarkdown from source from <https://fletcherpenney.net/multimarkdown/>, one user reported that in October 2020 the version in the Ubuntu repository was too old andid not work with mdtool.

Jekyll requires ruby, the installation process is described [on this page](https://jekyllrb.com/docs/installation/)

    $ sudo apt install ruby-full
