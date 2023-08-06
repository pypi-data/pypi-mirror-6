# encoding: utf-8

"""
General purpose functions that raise the abstraction level of interacting with
lxml.objectify elements.
"""

from __future__ import absolute_import

from lxml import etree, objectify

from pptx.oxml import oxml_parser
from pptx.oxml.ns import NamespacePrefixedTag


def child(element, child_tag_str):
    """
    Return the first direct child of *element* having tag matching
    *child_tag_str* or |None| if no such child element is present.
    """
    nsptag = NamespacePrefixedTag(child_tag_str)
    xpath = './%s' % child_tag_str
    matching_children = element.xpath(xpath, namespaces=nsptag.nsmap)
    return matching_children[0] if len(matching_children) else None


def Element(nsptag_str, nsmap=None):
    """
    Return a 'loose' lxml element having the tag specified by *nsptag_str*.
    *nsptag_str* must contain the standard namespace prefix, e.g. 'a:tbl'.
    The resulting element is an instance of the custom element class for this
    tag name if one is defined.
    """
    nsptag = NamespacePrefixedTag(nsptag_str)
    nsmap = nsmap if nsmap is not None else nsptag.nsmap
    return oxml_parser.makeelement(nsptag.clark_name, nsmap=nsmap)


def get_or_add(parent, nsptag_str):
    """
    Return the first direct child element of *parent* with tag matching
    *nsptag_str*. If no such child is found, a new one is created and
    returned.
    """
    _child = child(parent, nsptag_str)
    if _child is None:
        _child = SubElement(parent, nsptag_str)
    return _child


def serialize_part_xml(part_elm):
    # if xsi parameter is not set to False, PowerPoint won't load without a
    # repair step; deannotate removes some original xsi:type tags in core.xml
    # if this parameter is left out (or set to True)
    objectify.deannotate(part_elm, xsi=False, cleanup_namespaces=False)
    xml = etree.tostring(part_elm, encoding='UTF-8', standalone=True)
    return xml


def SubElement(parent, nsptag_str, **extra):
    """
    Return an lxml element having *nsptag_str*, newly added as a direct child
    of *parent*. The new element is appended to the sequence of children, so
    this method is not suitable if the child element must be inserted at a
    different position in the sequence. The class of the returned element is
    the custom element class for its tag, if one is defined. Additional
    named parameters defined on lxml ``makeelement()`` are accepted, such as
    attrib=attr_dct and e.g. ``visible='1'``.
    """
    nsptag = NamespacePrefixedTag(nsptag_str)
    return objectify.SubElement(
        parent, nsptag.clark_name, nsmap=nsptag.nsmap, **extra
    )
