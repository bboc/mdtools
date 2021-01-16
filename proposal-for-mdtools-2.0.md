# Proposal for mdtools 2.0

## Purpose

The purpose of this document is to identify a path forward for mdtools as a single-source publishing system for the S3 Practical Guide and other electronic publications.

### Known Areas of Improvement

In its current state, `mdtools`` has **5 main areas where it can be improved significantly**:

1.   **rigid document structure**: 
    1.   Introduction - main part - appendix
     2. file naming is tied to the names of the chapters (and duplicated in the actual title in the document)
    3. each file name can only exist exactly once over the whole document
    4. folders for introduction and appendix are on the same levels as folders for the "chapters"
2. the special features related to patterns are not separated from the main rendering engine
3. metaphors and names in the code are inconsistent
4. the architecture is not very elegant
5. the engines for slides are largely unused these days

On top of that, there's no multi-language support, but maybe that is an unnecessary layer of complexity.

### New Features

Over the last year or so, we have identified several new updates we want to make to the Practical Guide to make it more valuable to its users that cannot be achieved with the current version of `mdtools`:

1. We want to **add the Common Sense Framework** as a new part of the practical guide, on the same level as the patterns, that is not possible with the current structure. If that is resolved, the concepts and principles would also make a dedicated part instead of a part of the introduction.
2. We want to provide a better and responsive menu for the website that makes the full content accessible to the user.
3. We want a clickable pattern map that is rendered as html and works as an overlay on each page


### Constraints for the proposed changes
Implementing those features must adhere to the constraints:

1. **full translation must still be possible**, i.e. all English text must be translatable, and duplication (e.f. in pattern names should be avoided)
2. if the document structure changes, there should be a way for **redirecting web requests** to the new URL


## Proposal A: New Architecture and Design

1. **Generic Corre**: The application will have a core that handles rendering of generic documents, modelled on the document structure
2. **Plugin Support**: The application will support plugins so that it is simple to add specific behavior for specific applications (such as everything that relates to S# patterns in the Practical Guide)
- **Configuration as code**: the build process is configured via presets that are defined in a configuration file, so that the makefile is simple and identical for all languages

### Plugins

Plugins are required for:

- processing content when (in the mark-down processor)
- creating specific documents that are required for specific output formats (e.g. an index document)

For now, plugins would reside in a plugins folder in the mdtools repository, eventually mdtools should also support plugins in separate repositories.

Plugins are configured in a configuration file (see below).

### Configuration as code

All configuration for the build process will now be located in configuration files. 

-   `structure.yaml` contains all information about the structure of the content, including information that is required for rendering individual content nodes
-   project.yaml contains all configuration about the project and the build process:
    -   global settings: project language, urls, version
    -   presets for all output formats (including plugins to be used


### Presets (or document types)

A preset is a configuration object for a specific output format of a document, see this example. The actual format of that configuration will be determined during implementation

project.yaml should have a global section that defines base values, which can then be overridden in a preset, so that the document structure can be defined for all output formats, one or more output formats can use another structure definition.


	localization: localization.po
	site:
	  renderer: jekyll
	  root: /en/source/docs/
	  templates: 
	    - source: path/to-file.html
	      destination: destination-path/rendered.file
	  glossary: en/glossary.yaml 
	  index-template: en/website/_templates/index.md
	  section-index-template: en/website/_templates/pattern-index.md
	  introduction-template: en/website/_templates/introduction.md
	  plugins:
	    - mpd.foo.bar(x, y, z)


## Proposal B: A more flexible document and website structure

### Status Quo

This is the **current document structure**:

-   introduction
-   chapters
    -   chapter 1
        -   chapter 1 section 1
-    appendix

What is considered a **pattern** in the S3 Practical guide is implicit: it's all the documents inside the "chapters".

#### Current Source Structure

In the **file system** it looks like this

-   introduction
    -   section 1
    -   section 2
-   chapter 1
    -   chapter 1 section 1
-   appendix
    -   appendix section 1


This structure is implemented in `structure.yaml` as follows:

	content:
	  title: title
	  end: SKIP
	
	  introduction:
	    title: Introduction
	    slug: introduction
	    sections:
	      - title: Section 1
	        slug: section-1
	      - title: Section 2
	        slug: section-2	        
	
	  chapters:
	    - title: Chapter 1
	      slug: chapter-1
	      sections:
	        - title: Section 1 in Chapter 1
	          slug: section-1-in-chapter-1
	
	    - title: Chapter 2
	      slug: Chapter 2
	      sections:
	        - title: …
	          slug: …
	
	  appendix:
	    title: Appendix
	    slug: appendix
	    sections:
	    - title: Appendix Section 1
	      slug: appendix-section-1

#### Current Target Structure:

In the **website**, each section is rendered as a separate html file in the root folder of the website, and the introduction and parts of the appendix are compiled in a separate process (defined in the makefile of the practical guide)

In **LaTex**, the the document structure is generated from the headline levels:

-  Parts: introduction, appendix and the body of chapters ("The Patterns" in the practical guide)
-  Chapters: the individual documents inside the introduction and appendix, as well as the individual chapters (in the practical guide these are the pattern groups) defined under "chapters" are each rendered as one chapter
-  Sections: each pattern, and each subheader of a document in introduction and appendix are rendered as a section

 
The **ePub** contains 3 xhtml files, one for introduction, one for "chapters", and one for appendix.

### Disadvantages of the current structure

1. Titles have to be defined in the structure (for the sole purpose of creating links  for the pattern navigation)
2. no way to add additional content outside introduction and appendix that is not considered a pattern
3. folders do not reflect document structure
4. slugs and titles are tied together, and each change of a title requires changing the slug (which implies changing the URL)

### Proposed Structure

The proposed more flexible structure is quite simple:

-   Parts (e.g. "Introduction", "Concepts and Principles", "The Patterns", "Appendix")
    -   Chapters (e.g. each pattern group)
        -    Sections (e.g. each pattern, or any other section of a chapter)

Representation in the **file system**:

-   Parts: a folder with an index document that provides the document title (and may contain a macro that renders sub navigation with summaries etc.)
-   Chapters: 
    -   either as individual documents in the folder of the part
    -   or as a subfolder with an index document that provides the title for that section
    -   (it should be possible to mix both options in the same part so that expanding one chapter does not require changing other chapters of the same part)
-   Sections: a section is an individual document, the section title is extracted from that document


#### structure.yaml

In the current version, structure is used for 3 purposes:

1.   defining what goes into the document
2.   defining the order of chapters and sections
3   providing titles to the part of the rendering system that deals with structure (links, navigation etc.). 

In the new version, the structure only has to handle 1 and 2, but it can be used to define additional attributes for the content:

	config:
	  title: title
	  end: SKIP
	  attribute: value
	
	parts:
	  introduction:
	    chapters:
	      - chapter-1
	      - 
	        id: chapter-2
	        attribute: value
	        sections:
	          - section 1
	          - section 2

The resulting data structure is simple to parse and enrich with data that is extracted from the content files (such as  titles or summaries). The renderer can also be built directly on that data structure. 

`structure.yaml` can also be used to configure most of the build, including special content that is used for the website, plugins that should be used etc.

`structure.yaml` must not contain any translatable or language specific content, so that translations cannot break the rendering process. It will be moved out of the content folder.

Translatable content goes into `localization.pot`, language specific configuration goes into `config/project.yaml`.


#### Proposed Target Structure:

**website**: 

- each part is a directory with an index document, 
- each chapter is either one html file in the folder of its parent part, or –if the chapter contains sections – a subfolder with an index document
- sections are individual html-documents in the chapter's folder

In **LaTex**, the the document structure remains the same. 
 
The **ePub** will contain one xhtml files per part.

### Discussion of Alternatives

The project structure could be determined from the structure of the content files themselves, i.e. if they were stored in the form of a Jekyll site. Including and excluding documents could then be handled via specific variables set in a YAML front matter block. However, in that case the order of the sections – which is needed for menus and for other output formats –would still have to be defined in a configuration file somewhere. It makes more sense to have a specific structure file.


## Proposal for pattern related content


Each pattern will have a unique name, and it needs to be on section level. A pattern's name should be defined only in title of its file.


- how to identify patterns and pattern groups? tags

## Proposal C: Migration Plan

### Redirecting URLS

Since the new  structure is folder-based, all current URLs will be invalid, so they would need to be redirected. On GitHub pages, redirections can only happen in the frontend, i.e. a page at the old url has to handle redirection via header and javascript. See [this article](https://opensource.com/article/19/7/permanently-redirect-github-pages) for details.

Redirections will be defined in `redirections.yam` file that simply lists the old and the new URL:

redirections:
  - from: section-1
    to: /part-1/chapter-1/section1
- from: …
    to: …

Since currently all sections have a unique filename, the first version of the redirections can be derived from the new structure file with a simple script.

For each entry in the file one html page is created that handles that specific redirect. In the future, when section names change, they are simply added to the redirections file.

### Migration Steps

Changing the structure is the biggest change, which will be required for adding the CSF to the practical guide. This requires also a new menu for the website. A clickable pattern map can be implemented after that.

1. write code that handles the new structure
2. re-arrange new content and update structure.yaml
3. implement redirections
4. create redirection file
5. build new formats and test thoroughly
6. implement new menu system
7. backup crowdin files, disable crowdin upload
7. generate new content
8. deploy
9. move files in crowdin so that no translations are lost!
10. re-activate crowdin upload
11. dry run to see if everything works
12. create clickable pattern map


## Proposal D: Responsive Menu and Clickable Pattern Map

Inclue a responsible menu that is rendered from the `structure.yaml` (which might include tags like 'not-in-menu'). Use similar code for creating the clickable pattern overlay.
