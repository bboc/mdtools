# mdslides

A set of tools to build slide decks from reositories of Markdown files for use in Deckset and reveal.js.

A presentation is created from several groups that consist of one or more sections. Each section is a file that contains one or more slides separated by `---`):

- `title.md` - Contains at least the title slide
- `introduction/*` (optional) 
- `chapters/<chapter name>/*` the main body of the slide deck. Chapters and sections within chapters can be numbered automatically, and may contain special image slides at the beginning of each chapter.
- `closing/*` (optional)
- `end.md` - contains at least one closing slide

Groups are irrelevant for Deckstet, but each group becomes its own column in reveal.js.

Slide decks are created and manipulated through four commands:


* `mdslides compile <config> <source> <destination> [options] ` compiles Markdown sections into one file per group. These files may then be then processed by other commands.
* `mdslides build deckset|revealjs|wordpress <config> <source> <destination> --template=<template>` builds deckset or reveal.js presentations, or formats the slides for use with Wordpress (with the Jetpack plugin)
* `mdslides convert <source> <target> --template=<template>` converts one deckset file to reveal.js (horizontal sections)
* `mdslides skeleton <config> <target>` can build the folder structure with markdown files from a config file so you do not have to set this up for yourself. If you run this over an existing folders, only files not existing will be created.

A YAML file describes the order of chapters, and what sections will be included in what chapter. The file contains optional entries for introduction and closing slides, as well as a special section `chapter_order` where the order of the chapter is defined.


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


The resository for "S3 - All Patterns explained" serves as an example for the [file structure](https://github.com/S3-working-group/s3-all-patterns-explained/tree/master/src), the [config file](https://github.com/S3-working-group/s3-all-patterns-explained/blob/master/s3-all-patterns-explained.yaml) and a [build script](https://github.com/S3-working-group/s3-all-patterns-explained/blob/master/build-slides.sh) for building reveal.js, wordpress and Decset versions.

Each chapter, as well as the optional groups introduction and closing may contain an section `index.md` as a preamble,  which is automatically included. This section is not included in the numbering of the chapte's sections. 

Title slides as text or image (or both) can be generated for each chapter with commandline options.

Between introduction and chapters a set of illustrations for each chapter can be added (used for showing all patterns in groups in "S3- All Patterns Explained", probably less useful in other slide decks.)