# mdtools

mdtools is a set of commandline scripts for creating various output formats from a single source of (multi-)markdown files

You can find an introduction and documentation to mdtools in the example project, which is also the source of the Github page for this repository. 

The simples way for getting started with your own project is to copy the example project and play around with it.


## mdslides

A powerful set of tools to build slide decks from repositories of Markdown files for use in [Deckset](http://decksetapp.com), [reveal.js](http://lab.hakim.se/reveal-js) and Wordpress. This helps with reuse of slides and evolution of large decks, e.g. [Sociocracy 3.0 - All Patterns Explained](http://sociocracy30.org/slides/s3-all-patterns-explained.html).

See [the mdslides documentation](slides/slides.md) for more information.

## Image Update 

Update image references in MultiMarkdown files (while preserving Deckset formatting). This is helpful when maintaining a large set of illustrations used in a large number of markdown file, because it allows for changing the folder structure of the illustrations without having to worry about updating all the references. 

Usage: see `mdimg -h`


## mddiff

Output diff between two Markdown files as Critic Markup

Usage: see `mddiff -h`

## Upcoming

* file transclusion for Multimarkdown files (with error output for missing files) (currently located in [this repository]())
