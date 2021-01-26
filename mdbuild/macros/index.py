# -*- coding: utf-8 -*-
"""
A macro that renders indexes.
"""

from operator import attrgetter

from mdbuild.common import markdown2html


class IndexMacro(object):
    """
    Process index macros.
    """

    @classmethod
    def render(cls, structure, format, *args, **kwargs):
        """Create a (sorted) index of pages.

        Parameters:
            - tag: filter by tag before creating the index
            - root: only show children of one specific node (by slug)
            - sort: sort index by node attribute (mostly title)
            - force_format: force a specific format
            - style:
              - full: one entry per paragraph: title and summary
              - simple: a list with one entry per item
        Examples:
            {{index:tag=pattern,sort=title}} create an index for all entries tagged 'pattern'
            {{index:root=slug}} create an index of all children of node
            {{index:force_format=plain}} force a format (useful for
                content-specific templates, not so much for content file)

        sort and format default to None.
        root is processed before tag filter.
        """
        # get arguments
        tag_filter = kwargs.get('tag')
        sort = kwargs.get('sort')
        format = kwargs.get('force_format', format)
        root = structure

        if 'root' in kwargs:
            root = structure.find(kwargs['root'])
            if not root:
                print('WARNING: could not resolve item: {{index:root=', kwargs['root'], '}}')
                return "{{index:root=%s ERRROR UNKNOWN ROOT}}" % kwargs['root']

        # select which nodes to show
        nodes_to_show = []
        if tag_filter:
            current_node = root
            while current_node:
                if tag_filter in current_node.tags:
                    nodes_to_show.append(current_node)
                current_node = current_node.successor
        else:
            nodes_to_show = root.children[:]

        if sort:
            nodes_to_show.sort(key=attrgetter(sort))

        if format == 'html':
            return cls.render_html(nodes_to_show)
        else:  # plain list
            return cls.render_plain(nodes_to_show)

    @classmethod
    def render_plain(cls, nodes):
        INDEX_ELEMENT_PLAIN = "- [%(title)s](%(path)s.html)\n"
        res = []
        for node in nodes:
            res.append(INDEX_ELEMENT_PLAIN % dict(title=node.title, path=node.slug))
        return ''.join(res)

    @classmethod
    def render_html(cls, nodes):
        res = ["<dl>"]
        for node in nodes:
            res.append(cls.html_index_element(node.title, node.slug, node.summary))
        res.append("</dl>")
        return '\n'.join(res)

    # TODO: enventually use dedent, but it messes up the diffs while the rewrite is in progress
    INDEX_ELEMENT_HTML = """
  <dt><a href="%(path)s.html">%(title)s</a></dt>
  <dd>%(summary)s</dd>"""

    @classmethod
    def html_index_element(cls, title, path, summary):
        if summary:
            summary = markdown2html(summary)
        else:
            summary = ''
        return cls.INDEX_ELEMENT_HTML % locals()
