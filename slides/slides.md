# mdslides

A set of tools to build slide decks from repositories of Markdown files for use in [Deckset](https://www.decksetapp.com/) and [reveal.js](http://lab.hakim.se/reveal-js/#/).

A presentation is created from several groups that consist of one or more sections. Each section is a file that contains one or more slides separated by `---`:

- `title.md` - Contains at least the title slide, file name can be overridden in yaml
- `introduction/*` (optional) 
- `chapters/<chapter name>/*` the main body of the slide deck. Chapters and sections within chapters can be numbered automatically, and may contain special image slides at the beginning of each chapter.
- `closing/*` (optional)
- `end.md` - contains at least one closing slide, file name can be overridden in yaml

Groups are irrelevant for Deckset, but each group becomes its own column in reveal.js.

Slide decks are created and manipulated through four commands:

* `mdslides compile <config> <source> <destination> [options] ` compiles Markdown sections into one file per group. These files may then be then processed by other commands.
* `mdslides build deckset|revealjs|wordpress <config> <source> <destination> --template=<template>` builds Deckset or reveal.js presentations, or formats the slides for use with Wordpress (with the Jetpack plugin)
* `mdslides convert <source> <target> --template=<template>` converts one Deckset file to reveal.js (horizontal sections)
* `mdslides skeleton <config> <target>` can build the folder structure with markdown files from a config file so you do not have to set this up for yourself. If you run this over an existing folders, only files not existing will be created.

A YAML file describes the order of chapters, and what sections will be included in what chapter. The file contains optional entries for introduction and closing slides, as well as a special section `chapter_order` where the order of the chapter is defined.

    title: deck_title    
    introduction:
      - one section 
      - another section
    
    chapter_order:
      - one chapter
      - another chapter
      - a third chapter
    
    chapters:
      one chapter:
        - some very important things
        - a point to make 
        - some things best not left unsaid
      another chapter:
        - just one section here
      a third chapter:
        - this has one section
    
      end: end_slides


The repository for "S3 - All Patterns explained" serves as an example for the [file structure](https://github.com/S3-working-group/s3-all-patterns-explained/tree/master/src), the [config file](https://github.com/S3-working-group/s3-all-patterns-explained/blob/master/s3-all-patterns-explained.yaml) and a [build script](https://github.com/S3-working-group/s3-all-patterns-explained/blob/master/build-slides.sh) for building reveal.js, wordpress and Deckset versions.

Each chapter, as well as the optional groups introduction and closing may contain an section `index.md` as a preamble,  which is automatically included. This section is not included in the numbering of the chapter's sections. 

Title slides as text or image (or both) can be generated for each chapter with command line options.

Between introduction and chapters a set of illustrations for each chapter can be added (used for showing all patterns in groups in "S3- All Patterns Explained", probably less useful in other slide decks.)


## Notes about the glossary

Since a glossary is ordered alphabetically, if it were kept as a text document, a translation would be ordered incorrectly. To remedy this, a glossary can be stored in a yaml file, which also can contain definitions of terms for use in the slides.

The directive {{insert-full-glossary}} will insert a glossary, complete with headlines and slides markers. That way, the position of the glossary in the slide deck can easily be controlled.

The glossary has the following structure

  title: Glossary
  continued: (cont.)
  terms:
    accountability:
      name: name of the term
      definition: a definition of the term to be used in the text
      glossary: the text for the glossary entry
      note: an (optional) note to be appended to the glossary entry.


The text of a single glossary entry can be placed anywhere in the text with the directive {{glossary:term}}.  It's also possible to keep definitions in the glossary file, which can be placed in the text with the directive {{define:term}}. The benefit of this is that definitions and glossary entries need to be aligned, which is simple when they are kept next to each other in one file. 

The full glossary is rendered in the build step, as it depends on the output format, but the directives 'define' and 'glossary' are replaced in the compile step.


### Glossary Output

for HTML-Output, we need to render definition lists as html.

We can't use markdown definiton lists, because  they are not supported in reveal.js

Driver
: The dude who sits at the steering wheel


Relevant support:

-    reveal.js / GfM: **not supported**
-    deckset: **not suported**
-    Github Pages/kramdown (for future rendering through jekyll), see <https://kramdown.gettalong.org/syntax.html#definition-lists>
-    wordpress/markdown extra (https://michelf.ca/projects/php-markdown/extra/#def-list)
-    MMD: https://github.com/fletcher/MultiMarkdown/wiki/MultiMarkdown-Syntax-Guide#definition-lists

Number of glossary elements per page can be determined per commandline parameter `--glossary-items`, maybe later that will change to a rough nuber of words or similar, at least for some output formats.



