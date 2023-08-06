# This code was taken from... I think it's free as in Beer.
# http://nonplatonic.com/ben.php?title=python_xml_to_dict_bow_to_my_recursive_g

import xml.dom.minidom
import re

BAD_CHARS = re.compile(r'<>|</>')


def remove_bad_chars(data):
    return BAD_CHARS.sub('', data)


def xmltodict(xmlstring):
    xmlstring = remove_bad_chars(xmlstring)
    doc = xml.dom.minidom.parseString(xmlstring)
    remove_whilespace_nodes(doc.documentElement)
    return elementtodict(doc.documentElement)


def elementtodict(parent):
    child = parent.firstChild
    if (not child):
        return None
    elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
        return child.nodeValue

    d = {}
    while child is not None:
        if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
            try:
                d[child.tagName]
            except KeyError:
                d[child.tagName] = []
            d[child.tagName].append(elementtodict(child))
        child = child.nextSibling
    return d


def remove_whilespace_nodes(node, unlink=True):
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whilespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()
