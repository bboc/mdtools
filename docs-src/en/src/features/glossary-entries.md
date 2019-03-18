## Glossary

{{define:glossary}}

mdtools expects the glossary in a YAML-file, and can do a few tricks with it: 

- insert glossary explanations or definitions into the text using &#0123;&#0123;glossary:glossary-term&#0125;&#0125; or &#0123;&#0123;define:glossary-term&#0125;&#0125;
- render a full glossary using &#0123;&#0123;insert-full-glossary&#0125;&#0125;
- add an explanation for a [glossary](glossary:glossary) term as an overlay (in html output) using &#0091;glossary&#0093;&#0040;glossary:glossary&#0041;

---

## Glossary Format:

    terms:
      my-term:
    	name: My Term
	definition: what you want to display in the definition of the term
    glossary: what you want to put into the glossary

---

## Glossary Item Style (ebook only)

The ebook writer allows for replacing of glossary links with footnotes, plain text, LaTeX underline or custom formats

Simply add the commandline option `--glossary-style` for rendering glossary links
    - `--glossary-style=plain` (default) replaces links with the link title
    - `--glossary-style=footnotes` renders them as footnote references (and appends a list of footnotes at the into tmp-appendix.md)
    - `--glossary-style=underline` replaces links with LaTeX markup for underline

---

## Glossary Item Style (ebook only)

Any other string will passed to `--glossary-style` will be used a a template for replacing the glossary link. Make sure to escape backticks and slashes accordingly, e.g. ``--glossary-style="\`\\underline{{%(title)s}}\`{=latex}"``

Variables in the template are:

- title: the title of the link in the text
- term: the glossary term (identifier in the glossary yaml file)
- name: the name of the glossary term in the yaml file)
- description: the description of the glossary term