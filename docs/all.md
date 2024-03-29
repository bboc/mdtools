---
title: mdtools Documentation
---

### What is this?

_mdtools_ is a set of command line tools written in Python that to render markdown content into ebooks, slide decks and static websites you can host on any web server, or as a GitHub page.

You can read this documentation as a [slide deck](https://bboc.github.io/mdtools/slides.html) or as a [website]()

#### Usecases

The biggest use case at the moment is the [S3 Practical Guide](https://patterns-sociocracy30.org), the "official" documentation for Sociocracy 3.0. It's compiled from ~100 source files into static website, ebooks and pdfs, and translated into several languages.

I also use it for all my slide for trainings, workshops and conferences, some [examples are on slideshare](https://www.slideshare.net/BernhardBockelbrink/)



### Formats

_mdslides_ can render the output in various formats:

* Markdown for Deckset
* epub (using pandoc)
* a HTML file for reveal.js
* a PDF
* a static website using Jekyll



#### Deckset

Deckset is a presenter for markdown slides. It is nice for small slide decks, but lacks a few features one would want when creating larger decks. 

#### Jekyll

Jekyll is a static website generator, also which is used for creating github pages.


## Features


#### Glossary

_A **glossary** is collection of explanations for words the reader might not be familiar with._

mdtools expects the glossary in a YAML-file, and can do a few tricks with it: 

- insert glossary explanations or definitions into the text using _&#0123;&#0123;glossary:glossary-term&#0125;&#0125;_ or _&#0123;&#0123;define:glossary-term&#0125;&#0125;_
- render a full glossary using _&#0123;&#0123;insert-full-glossary&#0125;&#0125;_
- add an explanation for a <a href="glossary.html#entry-glossary" class="glossary-tooltip" data-toggle="tooltip" title="Glossary: A collection of explanations for words the reader might not be familiar with.">glossary</a> term as an overlay (in html output) using _&#0091;glossary&#0093;&#0040;glossary:glossary&#0041;_


#### Glossary Format:

    terms:
      my-term:
        name: My Term
        definition: what you want to display in the definition of the term
        glossary: what you want to put into the glossary


#### Glossary Item Style (ebook only)

The ebook writer allows for replacing of glossary links with footnotes, plain text, LaTeX underline or custom formats

Simply add the commandline option `--glossary-style` for rendering glossary links:

- `--glossary-style=plain` (default) removes the glossary link by replacing it with the link title
- `--glossary-style=footnotes` renders them as footnote references (and appends a list of footnotes into tmp-appendix.md)
- `--glossary-style=underline` replaces links with LaTeX markup for underline



#### Glossary Item Style (ebook only)


Variables in the template are:

- **title**: the title of the link in the text
- **term**: the glossary term (identifier in the glossary yaml file)
- **name**: the name of the glossary term in the yaml file)
- **description**: the description of the glossary term


#### Section Links

You can link to another section, e.g. the _section about the glossary_ using a section link of the format &#0091;link title&#0093;&#0040;section:section-slug&#0041;

Section links will be replaced with a link suitable for the output format, for some formats, which do not support link targets, it makes sense to render them only as text (e.g. in a Deckset slide deck)

#### Chapter Headers

{>>TODO: insert section about chapter headers <<}

#### Index Files

{>>TODO: explain automatic transfusion of chapter index files <<}

## Data Structure

_mdslides_ expects your content in specific directories, and relies on a set of configuration files. It also requires certain directories for temp files, which can be set up with a command in _mdslides_.



### Defining the Project Structure

The project structure is made up of individual content files nodes in a folder structure. Which files are included is defined in a simple yaml file, often called `structure.yaml`. The same files can be re-used in different structures.

Consider this example:

<pre>
foobar.md
foobar/foo.md
foobar/bar.md
foobar/baz.md
foobar/baz/something.md
part2.md
</pre>


The yaml file to render all these files would look like this:

<pre>
parts:
  - id: foobar
    parts: 
    - foo
    - bar
    - id: baz
      tags: [one-tag, another-tag]
      parts:
      - something
- part2
</pre>


The yaml file defines which files to include, and in what order. 

Things that go together can simple be grouped into folders. For some flexibility when growing a document, mdtools is looking in several places when it encounters a document node that sub-nodes, e.g. for a node `foobar` it looks for:

<pre>
foobar.md
foobar/index.md
foobar/foobar.md
foorbar/foobar_index.md
</pre>

Pick a style that makes sense for your usecase.



### Configuration

TODO: describe config format



### Templates

{>>TODO:  <<} 

### Macros

A macro ("macroinstruction") is a programmable pattern which translates a certain sequence of input into a preset sequence of output.

Macros can be registered to certain renderers, and can take parameters that control how they are expanded.

All macros look like this: _&#0123;&#0123;name:parameters&#0125;&#0125;_ 

Makros may take parameters. Two parameters are processed before the macro is executed:

- **only**: macro is executed _only_ for the specified preset(s)
- **skip**: macro is _skipped_ for the specified preset(s)

Presets are separated with '|'

Examples:

   &#0123;&#0123;index:ignore=jekyll|all-in-one&#0125;&#0125;_
   &#0123;&#0123;index:only=jekyll&#0125;&#0125;_

#### Custom Macros

Creating custom macros is easy, they only need to provide a render method:

    def render_my_macro(config, structure, *args, **kwargs):
        return "macros will be replaced with this text"


Macros have access to the project configuration and to the content structure, so that they can create indexes and links, and are able to react on configuration parameters.


Example: the index below is rendered via &#0123;&#0123;index:root=indexes,sort=title,style=list&#0125;&#0125;)

- [A searchable index](index-demo-searchable.html)
- [Index demo: Summaries](index-demo-summary.html)
- [The Index Macro](index-macro.html)
- [The Menu Macro](menu-macro.html)




### The Index Macro

<summary>The _index macro_ can render parts of the structure as an index in various styles and formats.</summary>

_&#0123;&#0123;index:root=node_name,tag=value,style=value,sort=value,only=value&#0125;&#0125;_ 

Render a subset of the structure as index. 

Parameters:

-   root: (optional) only show children of one specific node in the index
-   tag: filter index for nodes with a specific tag (filter is applied after root!)
-   style: how the index will look:
    - summary: one entry per paragraph: title and summary
    - list: a list with one entry per item
-   only: jekyll
-   sort: sort index by node attribute, e.g. title 
- force_format: force a specific format (e.g. plain)



### Index demo: Summaries

<summary>This page demonstrates a simple index with summaries</summary>

_mdtools_ picks up the contents of the &lt;summary&gt;-tag for each page, therefore the index macro can output summaries like so:

&#0123;&#0123;index:root=indexes,sort=title,style=summary&#0125;&#0125;

<dl>

  <dt><a href="index-demo-searchable.html">A searchable index</a></dt>
  <dd></dd>

  <dt><a href="index-demo-summary.html">Index demo: Summaries</a></dt>
  <dd></dd>

  <dt><a href="index-macro.html">The Index Macro</a></dt>
  <dd></dd>

  <dt><a href="menu-macro.html">The Menu Macro</a></dt>
  <dd></dd>
</dl>


### A searchable index

<summary>This page demonstrates a searchable index.</summary>

This obviously doesn't make sense in an ebook.

&#0123;&#0123;sort=title,style=searchable,only=jekyll&#0125;&#0125;




### The Menu Macro

… renders HTML for [SmartMenus for jQuery](https://www.smartmenus.org/)

for use in templates.

Code: &#0123;&#0123;html-menu&#0125;&#0125;


## Commands


### Makefile and Tempfolder

`mdbuild` typically does not create the final output formats but compiles the source files that are required by other tools (jekyll, latexmk, pandoc) for  rendering the output. For some formats a temporary folder is required, and the temp folder requires a bit of housekeeping.

A good practice way for bringing together preprocessing and rendering the final output is a [makefile](https://www.gnu.org/software/make/) that defines one rule per output format, and a rule for cleaning and setting up the temporary folder.  

`mdtools` containts a sample makefile and a sample project.yaml that demonstrate how this all fits togeter, as well as a sample buildscript that runs clean, setup, and build rules for all target formats in sequence. For most applications all it would take to get going is this:

1. set the desired output filename in config/local-conf
2. remove or comment the target formats that are not required

Then you can run `make <format>` to test one specific format, and `source build.sh` for a clean build of all formats. 



### mdbuild


`mdbuild` is the main build command for convertin the source into several target formats.

Usage: see `mdbuild -h`




### mdslides


**Note: this command is currently deactivated!!!

`mdslides` brings several commands for

* `compile` creates one Markdown file per chapter
* `build` builds the output in various _formats_
* `convert` converts a Deckset slide deck to reveal.js or to output for Wordpress (with Jetpack or another Markdown plugin)
* `skeleton` parses a config file and creates folders for chapters and files for sections
* `deckset-index` (deprecated) build a translatable index file (the new config format will make this obsolete)
* 'template' Inject translations (and optionally parameters from a config) into a template file.



### mdimg


`mdimg` brings two tools that are helpful when maintaining a large set of illustrations used in a large number of markdown file: 

* check for duplicates images
* update image references 

This allows for changing the folder structure of the illustrations without having to worry about updating all the references in your slide decks or other texts. 

The only prerequsite is that each image has an unique filename.

Usage: see `mdimg -h`




## Styles and Other Assets

<div class="card summary"><div class="card-body">The various output formats require certain styles and other assets, this part of the documentation explains where goes what.
</div></div>

Since this documentation makes use of all those formats, so you can find everything described here this repository.


<dl>

  <dt><a href="jekyll-builds.html">Styles and Assets for Jekyll/GitHub Pages</a></dt>
  <dd></dd>

  <dt><a href="reveal.js-builds.html">Styles and Assets for reveal.js Builds</a></dt>
  <dd></dd>
</dl>


### Styles and Assets for Jekyll/GitHub Pages

Unless it's replaced at build time via an entry in `config.presets.templates`, the following subdirectories of `docs` typicall contain templates and other resources for you site:

- `_includes`: partials to be included by the templates in `_layouts`
- `_layouts`: the templates for the different page or tsypes you can use in your site
- `_sass`:  SCSS paritals that are processed into a single CSS fle
- `css`: css files, either compiled by Jekyll, or added manually
- `js`:
- `menu`: files related to smartmenus

see the [Jekyll documentation](https://jekyllrb.com/docs/structure/) for more information.


### Styles and Assets for reveal.js Builds

The folder `docs/reveal.js` contains all files related to reveal.js builds.

However, the reveal.js-builder is currently broken. So sad.


### Translation

It is very simple to translate a _mdtools_ project into another language, as all translatable content is kept in a single directory and is stored in text files which all common translation platforms can easily pick up. 

Simply drop the translated content into a new project, and you're ready to go.

#### Translating Templates

If templates contain translatable content, simply store them inside the content directory, and copy them to where you need them in the makefile.

## Appendix


### Glossary

**Glossary:** A collection of explanations for words the reader might not be familiar with.






#### Changelog


##### v2.1.3 (2024-02-09)

-   proper rendering of markdown in html-summaries

##### v2.1.2 (2022-04-05)

-   fixed a bug that broke rendering of summaries for LaTeX

##### v2.1.1 (2022-02-27)

-   a couple of bug fixes

##### v2.1.0 (2022-02-22)

-   integration of Bootstrap 4
-   better and more responsive website layout
-   better rendering of summaries for ePub and site
-   nicer navigation buttons
-   removed support for _read-next-navigation_ and _read-next-shortcuts_ (because that can be achieved via CSS and editing the templates)


##### v2.0.2 (2021-09-28)

-   fixed page navigation
-   different rendering of tool-tips


##### v2.0.1 (2021-02-11)

-   fixed several bugs and glitches
-   documentation is building again (but not all new features are documented)
-   added Deckset renderer
-   added new glossary format for HTML: definition lists (CSS-class: glossary)
-   added new config-variables:
    -   read-next-navigation (default: false): add navigation below content pages
    -   read-next-shortcuts (default: false)
-   added support for included/skipping content blocks in specific formats, presets or editions
-   cleaner code


##### v2.0.0 (2021-02-03)

-   new version: `mdtools` 2.0.0
-   more flexible content structure that supports any number of parts and chapters, to just introduction, content and appendix.
-   configuration-as-code
    -   removed lots of dependencies on the idiosyncrasies of the S3 practical guide in favor of a more flexible configuration-as-code approach
    -   build behavior is defined in one YAML file that defines multiple output formats, with one global section and presets for each output format 
    -   template rendering can be defined in the config, which makes for a much simpler makefile 
-   extensible macro system
-   much simpler and cleaner code
-   **note**: for now, `mdtools` no longer supports building slide decks. This might be re-added later.


##### March 2019

* added command-line parameter --glossary-style for rendering glossary links in various formats, see documentation for details


##### August 2018

* fixed a bug in the section navigation on the Jekyll site
* added a GitHub page as a showcase that is built through `mdtools`
* added section links and overlays for glossary terms
* added basic tests for all output formats of `mdslides`


##### May 2018

* added a new sub-command 'templates' to `mdslides` to insert variables and translations into template files
 

##### February 2018

* added commands to build e-books (ePub and PDF from LaTex)


##### January 2018

* added basic section navigation to Jekyll site
* added translatable index and localization for Jekyll site


##### November 2017

* added support for glossaries


##### September 2017

* `mdimg` now handles images in multiple languages



### Alphabetical List Of All Pages

<dl>

  <dt><a href="appendix.html">Appendix</a></dt>
  <dd></dd>

  <dt><a href="commands.html">Commands</a></dt>
  <dd></dd>

  <dt><a href="data-structure.html">Data Structure</a></dt>
  <dd></dd>

  <dt><a href="features.html">Features</a></dt>
  <dd></dd>

  <dt><a href="formats.html">Formats</a></dt>
  <dd></dd>

  <dt><a href="macros.html">Macros</a></dt>
  <dd></dd>

  <dt><a href="styles-and-assets.html">Styles and Other Assets</a></dt>
  <dd><p>The various output formats require certain styles and other assets, this part of the documentation explains where goes what.</p></dd>

  <dt><a href="translation.html">Translation</a></dt>
  <dd></dd>

  <dt><a href="introduction.html">What is this?</a></dt>
  <dd></dd>
</dl>


### Markdown Cheat-Sheet and Theme Checker

<div class="card summary"><div class="card-body">This page contains most of the Markdown syntax elements and several macros, so that you can check if the output looks ok in the various output formats. It doesn't cover all the edge cases, but it provides a solid start.
</div></div>

(The above paragraph is tagged as summary!)


#### The Basics

In this paragraph you will find some **bold text**, and some *italicized text*, and some `code`. ~~This statement is false .~~[^1]

[^1]: This is the footnote.

The following text is a blockquote

> In a blockquote you might see something **important**, and something _emphasized._


#### Lists

Sometimes you want ordered lists:

1. First item
2. Second item
3. Third item

On other occasions an unordered list is all it takes.

- First item
- Second item
- Third item

However, sometimes there is more to say about some of the bullet points:

-   this one is simple
-   but this one
    -   requires more explanation
    -   because it is more complex
-   this one's more straightforward

You can also have a list of tasks:

- [x] that was easy
- [ ] this one is yet to be done
- [ ] this one will never be finished


#### Horizontal Rule

A horizontal rule:


(this text is below the horizontal rule)


#### Links and link-likes

Here's a _link to another page_, a link to a [heading on this page](#my-heading-id), and here's a term from the <a href="glossary.html#entry-glossary" class="glossary-tooltip" data-toggle="tooltip" title="Glossary: A collection of explanations for words the reader might not be familiar with.">glossary</a> (you should see a tool-tip on mouse-over)


#### Image

![This is the caption of the image above – a placeholder, just like the image itself.](/img/placeholder.png)


#### Definition List

this is the term
: and this is the definition of the term, hopefully that is enough explanation.


#### Table

Here's a simple table

| Column 1 | Column 2 |
| ----------- | ----------- |
| Row 1 | Row 2 |
| foo | bar |


#### Fenced Code Block

```python
import os

def myMethod(foo, bar):
    # ignore bar
    return foo
```

### All the Headings {#my-heading-id}

#### One More Heading

##### One More Heading

###### One More Heading

####### One More Heading

######## One More Heading


######### One More Heading?

No, that's it, it shouldn't go any deeper.


### Some Text to Demonstrate Page Width and Typography

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Id cursus metus aliquam eleifend. Viverra nibh cras pulvinar mattis nunc sed blandit. Elit duis tristique sollicitudin nibh sit amet commodo nulla. Eget nunc lobortis mattis aliquam. Risus viverra adipiscing at in tellus integer. Id cursus metus aliquam eleifend. Velit laoreet id donec ultrices tincidunt arcu non sodales neque. Porttitor leo a **diam sollicitudin** tempor id. Sed felis eget velit aliquet sagittis id consectetur purus. Pretium quam vulputate dignissim suspendisse in est ante in. Fames ac turpis egestas integer eget aliquet. Imperdiet nulla malesuada pellentesque elit eget gravida cum sociis natoque. Condimentum lacinia quis vel eros. [Mi quis hendrerit dolor magna](#) eget est lorem. Vel facilisis volutpat est velit egestas dui id ornare.

Augue mauris augue neque gravida in. Non tellus orci ac auctor augue mauris augue neque. Cras sed felis eget velit aliquet sagittis. Nunc aliquet bibendum enim facilisis gravida neque convallis a. Et sollicitudin ac orci phasellus egestas tellus rutrum. Odio tempor orci dapibus ultrices in iaculis. Sed vulputate odio ut enim. Quis lectus nulla at volutpat diam ut venenatis. Viverra justo nec ultrices dui sapien eget mi proin. Augue eget arcu dictum varius duis at consectetur. Turpis egestas maecenas pharetra convallis posuere morbi leo urna molestie. Dictumst quisque sagittis purus sit amet. Auctor neque vitae tempus quam pellentesque. Facilisi etiam dignissim diam quis enim lobortis.

Morbi tempus iaculis urna id volutpat. Nec sagittis aliquam malesuada bibendum arcu vitae elementum. Quis risus sed vulputate odio ut enim. Mollis nunc sed id semper risus in. _Tortor id aliquet lectus proin nibh nisl_. Vel eros donec ac odio tempor orci. Nibh venenatis cras sed felis eget velit aliquet sagittis id. Iaculis eu non diam phasellus vestibulum. Id cursus metus aliquam eleifend mi in. Nec nam aliquam sem et tortor consequat id. Quisque non tellus orci ac. Auctor eu augue ut lectus arcu bibendum at varius. Tortor dignissim convallis aenean et tortor at risus. Sagittis aliquam malesuada bibendum arcu vitae elementum curabitur. A lacus vestibulum sed arcu non odio euismod. Morbi tincidunt augue interdum velit euismod in. Quam elementum pulvinar etiam non. Adipiscing enim eu turpis egestas pretium aenean pharetra magna ac. Enim ut tellus elementum sagittis.


#### License

mdtools is licensed under the GNU General Public License v3.0

The full license is available under <https://github.com/bboc/mdtools/blob/master/LICENSE>

Contact me if you need another license for some reason.


