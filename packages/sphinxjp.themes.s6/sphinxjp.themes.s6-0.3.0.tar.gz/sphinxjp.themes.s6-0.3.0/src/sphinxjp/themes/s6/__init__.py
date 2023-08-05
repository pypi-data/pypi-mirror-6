# -*- coding: utf-8 -*-

from os import path
from sphinxjp.themes.s6 import directives

package_dir = path.abspath(path.dirname(__file__))
template_path = path.join(package_dir, 'templates')


def get_path():
    """entry-point for sphinxjp.themecore theme."""
    return template_path


def on_doctree_resolved(self, doctree, docname):
    if self.builder.name in ('singlehtml', 'html'):
        return

    for node in doctree.traverse(directives.s6_node):
        node.parent.remove(node)


def setup(app):
    """entry-point for sphinxjp.themecore directive."""
    directives.setup(app)
    app.connect("doctree-resolved", on_doctree_resolved)
    app.add_javascript('jquery.touchwipe.min.js')
    app.add_javascript('s6.js')
    app.add_javascript('s6-sphinx.js')
