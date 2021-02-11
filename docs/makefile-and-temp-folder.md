---
title: "Makefile and Tempfolder"
---


`mdbuild` typically does not create the final output formats but compiles the source files that are required by other tools (jekyll, latexmk, pandoc) for  rendering the output. For some formats a temporary folder is required, and the temp folder requires a bit of housekeeping.

A good practice way for bringing together preprocessing and rendering the final output is a [makefile](https://www.gnu.org/software/make/) that defines one rule per output format, and a rule for cleaning and setting up the temporary folder.  

`mdtools` containts a sample makefile and a sample project.yaml that demonstrate how this all fits togeter, as well as a sample buildscript that runs clean, setup, and build rules for all target formats in sequence. For most applications all it would take to get going is this:

1. set the desired output filename in config/local-conf
2. remove or comment the target formats that are not required

Then you can run `make <format>` to test one specific format, and `source build.sh` for a clean build of all formats. 



<div class="bottom-nav">
<a href="commands.html" title="Up: Commands">▲</a> <a href="mdbuild.html" title="">▶ Read next: mdbuild</a>
</div>


<script type="text/javascript">
Mousetrap.bind('g n', function() {
    window.location.href = 'mdbuild.html';
    return false;
});
</script>

