"""utils
Utility Fuctions for XCheck

"""

__history__="""
2013-10-05 - Rev 29 - added simple_formatter and debug_formatter for logging
"""

try:
    from elementtree import ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#utility functions
def get_bool(item):
    """get_bool(item)
    Return True if item is a Boolean True, 1, Yes, T, or Y
    Return False if item is a False, 0, No, F, or N
    Raises a ValueError if anything else

    get_bool() is case-insensitive.
    get_bool() raises a :py:exc:ValueError if item cannot be parsed.
    """

    if str(item).lower() in ['true','yes','1','t','y']:
        return True
    if str(item).lower() in ['false', 'no', '0', 'f', 'n']:
        return False
    raise ValueError("'%s' cannot be parsed into a boolean value" % item)

def get_elem(elem):
    """Assume an ETree.Element object or a string representation.
    Return the ETree.Element object"""
    if not ET.iselement(elem):
        try:
            elem = ET.fromstring(elem)
        except:
            raise ValueError("Cannot convert to element")

    return elem

def indent(elem, level=0):
    """indent(elem, [level=0])
    Turns an ElementTree.Element into a more human-readable form.

    indent is recursive.
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
        else:
            elem.tail="\n"

def list_requirements(checker, prefix=None):
    """
    lists the required attributes and children of a checker.
    Returns a list of tuples
    """
    res = []
    for att in checker.attributes.values():
        if att.required:
            if prefix:
                res.append(prefix + (att.name,))
            else:
                res.append((att.name,))

    for child in checker.children:
        if child.has_attributes:
            _prefix = (prefix + checker.name) if prefix else (checker.name)
            for att in child.attributes.values():
                res.append(prefix + (att.name,))
        if child.has_children:
            _prefix = (prefix + checker.name) if prefix else (checker.name,)
            res.extend(list_requirements(child, _prefix))
        elif child.min_occurs > 0:
            if prefix:
                res.append(prefix + (child.name,))
            else:
                res.append((child.name,))


    return res

#-------------------------------------------------------------------------------
# logging help

import logging
simple_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
_dstr = "%(name)s - %(levelname)s - %(message)s [%(module)s:%(lineno)d]"
debug_formatter = logging.Formatter(_dstr)
