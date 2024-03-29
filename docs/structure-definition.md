---
title: "Defining the Project Structure"
next_page_title: "Configuration"
next_page_url: "configuration.html"
prev_page_title: "Data Structure"
prev_page_url: "data-structure.html"
---


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

