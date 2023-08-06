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
_dstr = "%(name)s - %(levelname)s - %(message)s [%(module)s.%(funcName)s:%(lineno)d]"
debug_formatter = logging.Formatter(_dstr)

#-------------------------------------------------------------------------------
# Node Maniplation Tools
def insert_node(checker, parent, child):
    new_check, new_parent = drill_down_to_node(checker, parent, child)
    insert_child_into_node(new_check, new_parent, child)

def drill_down_to_node(checker, parent, child):
    """
    Starting at the parent node, return the node that should contain that
    child node, creating the nodes as needed.

    :param checker: the parent checker
    :type checker: xcheck object
    :param parent: the parent element
    :type parent: Element
    :param child: the child node
    :type child: Element
    """

    xpath = checker.xpath_to(child.tag)
    checker.logger.debug('drilling down to %s', xpath)

    if xpath is None:
        raise checker.error(
            "%sCheck cannot determine proper place for %s" % (checker.name, child.tag))

    if '@' in xpath:
        raise checker.error(
            "%sCheck cannot insert '%s' attribute as a child node" % (checker.name, child.tag))

    this_node = parent
    this_check = checker
    tags = xpath.split('/')
    tags.pop(0)
    while tags:

        this_tag = tags.pop(0)
        checker.logger.debug('looking for %s', this_tag)
        if this_tag == child.tag:
            checker.logger.debug('found what we are looking for')
            break
        acceptable_children = [ch.name for ch in this_check.children]

        #this may never be raised
        if this_tag not in this_check.child_names:
            raise checker.error("Cannot insert %s into %s" % (this_tag, this_check.name))

        known_children = [nd.tag for nd in this_node]
        if this_tag not in known_children:
            checker.logger.debug('Must create %s child', this_tag)
            lvl = this_check.logger.level
            this_check.logger.setLevel(checker.logger.level)
            insert_child_into_node(this_check, this_node, ET.Element(this_tag))
            this_check.logger.setLevel(lvl)



        next_check = this_check.get(this_tag)
        checker.logger.debug('next_check is %s', next_check)
        # bug? Sometimes next_check is not found
        if next_check is None:
            next_check = this_check.get('.%s' % this_tag)
        checker.logger.debug('next_check is %s', next_check)


        next_node = this_node.find(this_tag)

        this_check = next_check
        this_node = next_node

    return (this_check, this_node)

import itertools as I
def insert_child_into_node(checker, parent, child):
    """
    :param checker: XCheck object attached to parent
    :param parent: Element node
    :param child: Element node
    """
    if not checker.name == parent.tag:
        raise checker.error("Checker/Parent mismatch: %s, %s" % (checker, parent))

    checker.logger.debug('Acceptable children: [%s]', ' '.join(checker.child_names))
    if child.tag not in checker.child_names:
        raise checker.error(
            "%sCheck object cannot have %s as child" % (
                checker.name, child.tag))

    known_children = [nd.tag for nd in parent]

    if not known_children:
        checker.logger.debug('No children -- appending')
        parent.append(child)
        return True

    checker.logger.debug('Known children: [%s]', ' '.join(known_children))

    child_check = checker.get(child.tag)
    checker.logger.debug('Need %sCheck, found %s' % (child.tag, child_check))

    if known_children.count(child.tag) >= child_check.max_occurs:
        raise child_check.error("Too many %s children (%d already, no more than %d)" %
            (child.tag, known_children.count(child.tag), child_check.max_occurs))

    child_index = 0
    pre_tag = True
    in_tag = False

    checker.logger.debug('%sCheck acceptable children: [%s]',
        checker.name,
        ' '.join(checker.child_names))

    tags_preceding_child = list(
        I.dropwhile(lambda x: x != child.tag, checker.child_names))
    checker.logger.debug('remaining children: %s', tags_preceding_child)

    tags_after_child = list(
        I.dropwhile(lambda x: x == child.tag, tags_preceding_child))
    checker.logger.debug('remaining children: %s', tags_after_child)


    ins = None
    for tag_to_find in tags_after_child:
        if tag_to_find in known_children:
            ins = known_children.index(tag_to_find)
            checker.logger.debug('setting ins to %d', ins)
            break
    if ins is None:
        checker.logger.debug('fallback - appending child')
        parent.append(child)
        return True

    parent.insert(ins, child)
    return True