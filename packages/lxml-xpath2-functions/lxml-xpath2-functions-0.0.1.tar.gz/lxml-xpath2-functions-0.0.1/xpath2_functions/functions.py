"""
Set of Xpath2 functions which you can register in lxml.

.. author:: Kamil Kujawinski <kamil@kujawinski.net>
"""
from lxml.etree import _Element


def textify_node(node):
    if isinstance(node, _Element):
        return node.xpath('.//text()')[0]
    else:
        return node


def string_join(context, items, separator):
    items = [textify_node(i) for i in items]
    return separator.join(items)


ALL_FUNCTIONS = {
    'string-join': string_join,
}

