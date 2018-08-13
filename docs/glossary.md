---
title: "Glossary"
---


{{definition:glossary}}

mdtools expects the glossary in a YAML-file, and can do a few tricks with it: 

- insert glossary explanations or definitions into the text
- render a full glossary
- add an explanation for a <dfn data-info="Glossary: A collection of explanations for words the reader might not be familiar with.">glossary</dfn> term as an overlay (in html output)


## Glossary Format:

    terms:
      my-term:
    	name: My Term
	definition: what you want to display in the definition of the term
    glossary: what you want to put into the glossary



[&#9654; Section Links](section-links.html)<br/>[&#9650; Features](features.html)

