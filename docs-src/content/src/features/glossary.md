## Glossary

{{definition:glossary}}

mdtools expects the glossary in a YAML-file, and can do a few tricks with it: 

- insert glossary explanations or definitions into the text
- render a full glossary
- add an explanation for a [glossary](glossary:glossary) term as an overlay (in html output)

---

## Glossary Format:

    terms:
      my-term:
    	name: My Term
	definition: what you want to display in the definition of the term
    glossary: what you want to put into the glossary

