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

