# Check your theme

This page contains most of the Markdown syntax elements and several macros, so that you can check if the output looks ok in the various output formats. It doesn't cover all the edge cases, but it provides a solid start.

## The Basics


In this paragraph you will find some **bold text**, and some *italicized text*, and some `code`. ~~This statement is false .~~[^1]

[^1]: This is the footnote.

The following text is a blockquote

> In a blockquote you might see something **important**, and something _emphasized._

Sometimes you want ordered lists:

1. First item
2. Second item
3. Third item

On other occasions an unordered list is all it takes.

- First item
- Second item
- Third item

However, sometimes there is more to say about some of the bullet points:

-   this one is simple
-   but this one
    -   requires more explanation
    -   because it is more complex
-   this one's more straightforward

You can also have a list of tasks:

- [x] that was easy
- [ ] this one is yet to be done
- [ ] this one will never be finished


## Horizontal Rule

A horizontal rule:

---

(this text is below the horizontal rule)


## Links and link-likes

Here's a [link to another page](section:appendix), a link to a [heading on this page](#my-heading-id), and here's a term from the [glossary](glossary:glossary) (you should see popover on mouseover)


## Image

![alt text](/img/placeholder.png)


## Definition List

term
: definition


## Table

Here's a simple table

| Column 1 | Column 2 |
| ----------- | ----------- |
| Row 1 | Row 2 |
| foo | bar |


## Fenced Code Block

```python
import os

def myMethod(foo, bar):
    # ignore bar
    return foo
```

# All the headings {#my-heading-id}

## one more heading

### one more heading

#### one more heading

##### one more heading

###### one more heading

####### one more heading

That's it, it shouldn't go any deeper.


