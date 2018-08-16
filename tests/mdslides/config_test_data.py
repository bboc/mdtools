# -*- coding: utf-8 -*-

from textwrap import dedent

extended_format = dedent("""

    section-prefix: "%(chapter)s.%(section)s:"
    content:
        title: title
        end: SKIP
        introduction:
            title: Introduction
            slug: introduction
            sections:
                - overview
                - usecases
        chapters:
            - formats:
                - deckset
                - jekyll
            - features:
                - title: Glossary Entries
                  slug: glossary-entries
                - section links
                - chapter headers
                - index files
            - title: Data Structure
              slug: data-structure
              sections:
                - title: Templates
                  slug: templates
            - commands:
                - mdslides
                - mdimg
            - translation:
                - translating templates
        appendix:
            - glossary
            - changelog
            - license
 """)

simple_format = dedent("""
    title: title
    end: SKIP

    section-prefix: "%(chapter)s.%(section)s:"

    introduction:
        - overview
        - usecases

    appendix:
        - glossary
        - changelog
        - license

    chapter-order:
        - formats
        - features
        - data structure
        - commands
        - translation

    chapters:
        formats:
            - deckset
            - jekyll
        features:
            - glossary entries
            - section links
            - chapter headers
            - index files
        data structure:
            - templates
        commands:
            - mdslides
            - mdimg
        translation:
            - translating templates
""")

result = {
    'content': {'appendix': {'sections': [{'id': 1,
                                           'slug': 'glossary',
                                           'title': 'Glossary'},
                                          {'id': 2,
                                           'slug': 'changelog',
                                           'title': 'Changelog'},
                                          {'id': 3,
                                           'slug': 'license',
                                           'title': 'License'}],
                             'slug': 'appendix',
                             'title': 'Appendix'},
                'chapters': [{'id': 1,
                              'sections': [{'chapter_id': 1,
                                            'id': 1,
                                            'slug': 'deckset',
                                            'title': 'Deckset'},
                                           {'chapter_id': 1,
                                            'id': 2,
                                            'slug': 'jekyll',
                                            'title': 'Jekyll'}],
                              'slug': 'formats',
                              'title': 'Formats'},
                             {'id': 2,
                              'sections': [{'chapter_id': 2,
                                            'id': 1,
                                            'slug': 'glossary-entries',
                                            'title': 'Glossary Entries'},
                                           {'chapter_id': 2,
                                            'id': 2,
                                            'slug': 'section-links',
                                            'title': 'Section Links'},
                                           {'chapter_id': 2,
                                            'id': 3,
                                            'slug': 'chapter-headers',
                                            'title': 'Chapter Headers'},
                                           {'chapter_id': 2,
                                            'id': 4,
                                            'slug': 'index-files',
                                            'title': 'Index Files'}],
                              'slug': 'features',
                              'title': 'Features'},
                             {'id': 3,
                              'sections': [{'chapter_id': 3,
                                            'id': 1,
                                            'slug': 'templates',
                                            'title': 'Templates'}],
                              'slug': 'data-structure',
                              'title': 'Data Structure'},
                             {'id': 4,
                              'sections': [{'chapter_id': 4,
                                            'id': 1,
                                            'slug': 'mdslides',
                                            'title': 'Mdslides'},
                                           {'chapter_id': 4,
                                            'id': 2,
                                            'slug': 'mdimg',
                                            'title': 'Mdimg'}],
                              'slug': 'commands',
                              'title': 'Commands'},
                             {'id': 5,
                              'sections': [{'chapter_id': 5,
                                            'id': 1,
                                            'slug': 'translating-templates',
                                            'title': 'Translating Templates'}],
                              'slug': 'translation',
                              'title': 'Translation'}],
                'end': None,
                'index': [{'chapter_id': 2,
                           'id': 3,
                           'slug': 'chapter-headers',
                                   'title': 'Chapter Headers'},
                          {'chapter_id': 1,
                           'id': 1,
                           'slug': 'deckset',
                                   'title': 'Deckset'},
                          {'chapter_id': 2,
                           'id': 1,
                           'slug': 'glossary-entries',
                                   'title': 'Glossary Entries'},
                          {'chapter_id': 2,
                           'id': 4,
                           'slug': 'index-files',
                                   'title': 'Index Files'},
                          {'chapter_id': 1,
                           'id': 2,
                           'slug': 'jekyll',
                                   'title': 'Jekyll'},
                          {'chapter_id': 4,
                           'id': 2,
                           'slug': 'mdimg',
                                   'title': 'Mdimg'},
                          {'chapter_id': 4,
                           'id': 1,
                           'slug': 'mdslides',
                                   'title': 'Mdslides'},
                          {'chapter_id': 2,
                           'id': 2,
                           'slug': 'section-links',
                                   'title': 'Section Links'},
                          {'chapter_id': 3,
                           'id': 1,
                           'slug': 'templates',
                                   'title': 'Templates'},
                          {'chapter_id': 5,
                           'id': 1,
                           'slug': 'translating-templates',
                                   'title': 'Translating Templates'}],
                'introduction': {'sections': [{'id': 1,
                                               'slug': 'overview',
                                               'title': 'Overview'},
                                              {'id': 2,
                                               'slug': 'usecases',
                                               'title': 'Usecases'}],
                                 'slug': 'introduction',
                                 'title': 'Introduction'},
                'title': 'title'},
    'section-prefix': '%(chapter)s.%(section)s:'}
