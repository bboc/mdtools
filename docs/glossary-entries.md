---
title: "Glossary"
---


_A **glossary** is collection of explanations for words the reader might not be familiar with._

mdtools expects the glossary in a YAML-file, and can do a few tricks with it: 

- insert glossary explanations or definitions into the text using _&#0123;&#0123;glossary:glossary-term&#0125;&#0125;_ or _&#0123;&#0123;define:glossary-term&#0125;&#0125;_
- render a full glossary using _&#0123;&#0123;insert-full-glossary&#0125;&#0125;_
- add an explanation for a <dfn data-info="Glossary: A collection of explanations for words the reader might not be familiar with.">glossary</dfn> term as an overlay (in html output) using _&#0091;glossary&#0093;&#0040;glossary:glossary&#0041;_


## Glossary Format:

    terms:
      my-term:
        name: My Term
        definition: what you want to display in the definition of the term
        glossary: what you want to put into the glossary


## Glossary Item Style (ebook only)

The ebook writer allows for replacing of glossary links with footnotes, plain text, LaTeX underline or custom formats

Simply add the commandline option `--glossary-style` for rendering glossary links:

- `--glossary-style=plain` (default) removes the glossary link by replacing it with the link title
- `--glossary-style=footnotes` renders them as footnote references (and appends a list of footnotes into tmp-appendix.md)
- `--glossary-style=underline` replaces links with LaTeX markup for underline



## Glossary Item Style (ebook only)


Variables in the template are:

- **title**: the title of the link in the text
- **term**: the glossary term (identifier in the glossary yaml file)
- **name**: the name of the glossary term in the yaml file)
- **description**: the description of the glossary term


<div class="bottom-nav">
<a href="features.html" title="Up: Features">▲</a> <a href="section-links.html" title="">▶ Read next: Section Links</a>
</div>


<script type="text/javascript">
Mousetrap.bind('g n', function() {
    window.location.href = 'section-links.html';
    return false;
});
</script>

