---
title: "Changelog"
next_page_title: "Alphabetical List Of All Pages"
next_page_url: "site-index.html"
prev_page_title: "Glossary"
prev_page_url: "glossary.html"
---



### v2.1.3 (2024-02-09)

-   proper rendering of markdown in html-summaries

### v2.1.2 (2022-04-05)

-   fixed a bug that broke rendering of summaries for LaTeX

### v2.1.1 (2022-02-27)

-   a couple of bug fixes

### v2.1.0 (2022-02-22)

-   integration of Bootstrap 4
-   better and more responsive website layout
-   better rendering of summaries for ePub and site
-   nicer navigation buttons
-   removed support for _read-next-navigation_ and _read-next-shortcuts_ (because that can be achieved via CSS and editing the templates)


### v2.0.2 (2021-09-28)

-   fixed page navigation
-   different rendering of tool-tips


### v2.0.1 (2021-02-11)

-   fixed several bugs and glitches
-   documentation is building again (but not all new features are documented)
-   added Deckset renderer
-   added new glossary format for HTML: definition lists (CSS-class: glossary)
-   added new config-variables:
    -   read-next-navigation (default: false): add navigation below content pages
    -   read-next-shortcuts (default: false)
-   added support for included/skipping content blocks in specific formats, presets or editions
-   cleaner code


### v2.0.0 (2021-02-03)

-   new version: `mdtools` 2.0.0
-   more flexible content structure that supports any number of parts and chapters, to just introduction, content and appendix.
-   configuration-as-code
    -   removed lots of dependencies on the idiosyncrasies of the S3 practical guide in favor of a more flexible configuration-as-code approach
    -   build behavior is defined in one YAML file that defines multiple output formats, with one global section and presets for each output format 
    -   template rendering can be defined in the config, which makes for a much simpler makefile 
-   extensible macro system
-   much simpler and cleaner code
-   **note**: for now, `mdtools` no longer supports building slide decks. This might be re-added later.


### March 2019

* added command-line parameter --glossary-style for rendering glossary links in various formats, see documentation for details


### August 2018

* fixed a bug in the section navigation on the Jekyll site
* added a GitHub page as a showcase that is built through `mdtools`
* added section links and overlays for glossary terms
* added basic tests for all output formats of `mdslides`


### May 2018

* added a new sub-command 'templates' to `mdslides` to insert variables and translations into template files
 

### February 2018

* added commands to build e-books (ePub and PDF from LaTex)


### January 2018

* added basic section navigation to Jekyll site
* added translatable index and localization for Jekyll site


### November 2017

* added support for glossaries


### September 2017

* `mdimg` now handles images in multiple languages

