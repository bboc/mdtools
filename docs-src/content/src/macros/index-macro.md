# The Index Macro

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

