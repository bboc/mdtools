# -*- coding: utf-8 -*-
"""
A macro that renders indexes.
"""

import logging
from operator import attrgetter

from mdbuild.common import markdown2html


logger = logging.getLogger(__name__)


class IndexMacro(object):
    """
    Process index macros.
    """

    @classmethod
    def render(cls, config, structure, *args, **kwargs):
        """Create a (sorted) index of pages.

        Parameters:
            - tag: filter by tag before creating the index
            - root: only show children of one specific node (by slug)
            - sort: sort index by node attribute (mostly title)
            - force_format: force a specific format
            - style:
              - summary: one entry per paragraph: title and summary
              - list: a list with one entry per item
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
        format = kwargs.get('force_format', config.target_format)
        style = kwargs.get('style', 'list')
        root = structure

        # find rood node for index
        if 'root' in kwargs:
            root = structure.find(kwargs['root'])
            if not root:
                logger.warning("could not resolve item: {{index:root='%s'}}" % kwargs['root'])
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
            nodes_to_show = root.parts[:]

        if sort:
            nodes_to_show.sort(key=attrgetter(sort))

        if style == 'summary':
            if format in ('html', 'epub'):
                return cls.render_html(nodes_to_show)
            elif format == 'latex':
                return cls.render_markdown(nodes_to_show, cls.LATEX_SUMMARY_TEMPLATE)
            else:  # markdown
                return cls.render_markdown(nodes_to_show, cls.MD_SUMMARY_TEMPLATE)
        else:  # list format
            return cls.render_markdown(nodes_to_show, cls.MD_LIST_TEMPLATE)

    LATEX_SUMMARY_TEMPLATE = "**%(title)s:** %(summary)s\n\n"
    MD_LIST_TEMPLATE = "- [%(title)s](%(slug)s.html)\n"
    MD_SUMMARY_TEMPLATE = "**[%(title)s](%(slug)s.html)**\n\n%(summary)s\n\n"

    @classmethod
    def render_markdown(cls, nodes, template):
        res = []
        for node in nodes:
            res.append(template % node.to_dict())
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


class MenuMacro(object):
    """
    Render a nested list for use in a menu.

    Rendering starts with <li>, because:

    - css classes of the outmost <ul> element
      can be defined in the html template
    - the menu can be extended easily in the html template
      by prepending and appending more elements.
    """

    @classmethod
    def render(cls, config, structure, *args, **kwargs):
        if not structure.parts:
            raise Exception("Can't render menu, menu parent has no parts!")
        try:
            noob_menu = config.noob_menu
        except AttributeError:
            noob_menu = False
        return '\n'.join(cls.render_parts(structure, [], noob_menu=noob_menu))

    @classmethod
    def render_parts(cls, node, res, noob_menu=False):
        for part in node.parts:
            if 'menu-title' in part.metadata:
                title = part.metadata['menu-title']
            else:
                title = part.title
            item_html = """<li><a href="%s.html">%s</a>\n""" % (part.slug, title)
            res.append(item_html)
            if part.parts:
                res.append("<ul>\n")
                if noob_menu:
                    # upon popular request: repeat parent inside each submenu
                    res.append(item_html)
                cls.render_parts(part, res, noob_menu)
                res.append("</ul>\n")
            res.append("</li>\n")
        return res
