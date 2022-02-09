---
title: "Macros"
---


A macro ("macroinstruction") is a programmable pattern which translates a certain sequence of input into a preset sequence of output.

Macros can be registered to certain renderers, and can take parameters that control how they are expanded.

All macros look like this: _&#0123;&#0123;name:parameters&#0125;&#0125;_ 

Makros may take parameters. Two parameters are processed before the macro is executed:

- **only**: macro is executed _only_ for the specified preset(s)
- **skip**: macro is _skipped_ for the specified preset(s)

Presets are separated with '|'

Examples:

   &#0123;&#0123;index:ignore=jekyll|all-in-one&#0125;&#0125;_
   &#0123;&#0123;index:only=jekyll&#0125;&#0125;_

### Custom Macros

Creating custom macros is easy, they only need to provide a render method:

    def render_my_macro(config, structure, *args, **kwargs):
        return "macros will be replaced with this text"


Macros have access to the project configuration and to the content structure, so that they can create indexes and links, and are able to react on configuration parameters.


Example: the index below is rendered via &#0123;&#0123;index:root=indexes,sort=title,style=list&#0125;&#0125;)

- [A searchable index](index-demo-searchable.html)
- [Index demo: Summaries](index-demo-summary.html)
- [The Index Macro](index-macro.html)
- [The Menu Macro](menu-macro.html)




<div class="bottom-nav">
<a href="templates.html" title="Back to: Templates">◀</a> <a href="index-macro.html" title="Read next: The Index Macro">▶ Read next: The Index Macro</a>
</div>


<script type="text/javascript">
Mousetrap.bind('g n', function() {
    window.location.href = 'index-macro.html';
    return false;
});
</script>

