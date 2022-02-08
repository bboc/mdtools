---
title: "Index demo: Summaries"
---


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
</dl>


<div class="bottom-nav">
<a href="index-macro.html" title="Back to: The Index Macro">◀</a> <a href="indexes.html" title="Up: Indexes">▲</a> <a href="index-demo-searchable.html" title="Read next: A searchable index">▶ Read next: A searchable index</a>
</div>


<script type="text/javascript">
Mousetrap.bind('g n', function() {
    window.location.href = 'index-demo-searchable.html';
    return false;
});
</script>

