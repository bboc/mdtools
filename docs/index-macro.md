---
title: "The Index Macro"
---


<summary>An explanation of the various parameters of the index macro</summary>

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



<div class="bottom-nav">
<a href="indexes.html" title="Up: Indexes">▲</a> <a href="index-demo-summary.html" title="Read next: Index demo: Summaries">▶ Read next: Index demo: Summaries</a>
</div>


<script type="text/javascript">
Mousetrap.bind('g n', function() {
    window.location.href = 'index-demo-summary.html';
    return false;
});
</script>

