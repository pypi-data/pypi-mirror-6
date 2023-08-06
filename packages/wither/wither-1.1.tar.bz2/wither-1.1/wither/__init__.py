#!/usr/bin/env python
"""Wither: Simple python DSL for writing XML/HTML

Wither is implemented as a thin stateless wrapper around lxml/etree nodes to 
provide a convient interface to create and update elements. the actual tree of 
nodes/elements is created and managed by etree objects and any node's backing 
object can be retrived by calling :py:func:`etree` on the node. this allows you 
to use standard etree functions such as tostring on the document or to retrive 
the more advanced node iterators

If you have an etree node that you wish to add elements to simply call 
:py:class:`Node` (etree_node) with the etree object procded as the first 
argument
"""
__author__ = "Da_Blitz"
__email__ = "code@pocketnix.org"
__url__ = "http://code.pocketnix.org/wither"
__version__ = "1.1"

import lxml.etree as _etree

class Node(object):
    """Node tags, attributes and text are prefixed with "node\_" to avoid potential 
    name conflicts with automatic object create. ie you may wish to create a 
    node called :py:meth:`attrib` or :py:meth:`text` or :py:meth:`tag` 
    however they would have been shadowed by the nodes properties
    
    to update xml attributes the prefered form is to use the python mapping 
    interface (ie obj[key]) on the node, however the attributes of the xml 
    fragment are also made avalible at node.node_attrib if you require the more 
    advanced dictonary methods such as itertion interfaces or dict.update()

    # enable XML literals in doctest output
    
    >>> import lxml.usedoctest

    Setting Attributes:

    Below is an example of updating the 'href' attribute in a link
    
    >>> a = Node('a')
    >>> a['href'] = 'http://www.example.org'
    >>> print(a)
    <a href="http://www.example.org"/>
    
    We also support setting kwargs via calling the proxy or in the proxy's 
    constructor, note that this returns the proxy itself for use inside a 
    'with' block
    
    >>> a = Node('a', href='http://www.example.org')
    >>> print(a)
    <a href="http://www.example.org"/>
    >>> a(href='http://www.example.com') # now change .org to .com
    <wither.Node object at ...>
    >>> print(a)
    <a href="http://www.example.com"/>
    
    Setting Text Nodes:

    this can be combined with setting of the text node via '==' (we use
    '==' instead of '=' as objects cannot override the assignment opperator)
    
    >>> a = Node('a')
    >>> print(a(href='http://www.example.org') == 'RFC2606 compliant')
    <a href="http://www.example.org">RFC2606 compliant</a>
    
    Sub Nodes/Elements:

    To Build new child nodes off of the current node, you can use standard 
    attribute access as shown below, repeated access to the same attribute 
    returns NEW objects, not the first one generated
    
    >>> div = Node('div')
    >>> div.p == 'this is the first paragraph'
    <...>
    >>> div.p == 'this is an entirely new (2nd) paragraph'
    <...>
    >>> print(div)
    <div><p>this is the first paragraph</p><p>this is an entirely new (2nd) 
    paragraph </p></div>
    
    With Blocks:

    With blocks can be used to add depth to a generated XML document. there is 
    no hard coded limit to the depth of the with statements, however for clarity 
    it is recommended that leaf nodes are created not via 'with parent.leaf as 
    leaf' but instead as 'parent.leaf(\*\*attribs) == "text"' to make leaf nodes 
    visually distinct and reduce the amount of indentation
    
    >>> n = Node('html')
    >>> with n.head as head:
    ...     head.title == 'Wither DocString Example'
    ...     head.link(href='http://www.example.org/', rel='homepage')
    <...>
    >>> print(n)
    <html><head><title>Wither DocString Example</title><link 
    href="http://www.example.org/" rel="homepage"/></head></html>
    """
    __slots__ = ('_node',)
    def __init__(self, tag, **attribs):
        """Node objects can be created by specifying tag as a string or by 
        providing a pre-created etree object to be used as the backing store. 
        the second form is mainly intended to convert a descendent etree node 
        back into a Node object for further manipulation of the tree after 
        performing an etree operation on a ancestor node
        
        :param tag: the tag to use as the tag for the etree backing store or a 
        prebuild etree object
        :type tag: str or etree.Element
        :param attrib: XML attributes specfied in the python keyword argument 
        format (href='http://www.example.org')
        """
        if isinstance(tag, str):
            self._node = _etree.Element(tag)
        else:
            self._node = tag
        
        self._node.attrib.update(attribs)
        
    @property
    def node_attrib(self):
        """Alternate way to add/set/delete XML attributes or access more 
        advanced dictonary methods for the attirbutes (eg 
        node_attrib.update()"""
        return self._node.attrib
    
    @property
    def node_tag(self):
        """The nodes tag property, eg 'div' for <div /> or 'a' for html 
        links"""
        return self._node.tag
    
    @property
    def node_text(self):
        """Allows setting of the XML tag's text property. eg <a 
        href="#link">The text property goes in here</a>
        """
        return self._node.text
        
    @node_text.setter
    def node_text(self, val):
        self._node.text = val

    def append(self, node):
        """Allows adding of foreign trees as children of this node
        
        >>> div = Node('div')
        >>> div.append(Node('p'))
        >>> len(div)
        1
        
        :param node Node: The node/foreign tree to be added
        """
        node = etree(node)
        self._node.append(node)
    
    def __getitem__(self, key):
        """Proxy item requests to self.node_attrib
        >>> n = Node('a')
        >>> n['href'] = 'http://www.example.org'
        >>> n['href']
        'http://www.example.org'
        """
        return self._node.attrib[key]
        
    def __setitem__(self, key, val):
        """Proxy item requests to self.node_attrib
        >>> n = Node('a')
        >>> n['href'] = 'http://www.example.org'
        >>> n['href']
        'http://www.example.org'
        """
        self._node.attrib[key] = val
        
    def __delitem__(self, key):
        """Proxy item deletions to self.node_attrib
        >>> n = Node('a')
        >>> n['href'] = 'http://www.example.org'
        >>> n['href']
        'http://www.example.org'
        >>> del n['href']
        >>> n['href']
        Traceback (most recent call last):
        KeyError: 'href'
        """
        del self._node.attrib[key]
        
    def __getattr__(self, tag):
        """Dynamically create Node objects with a tag name identical to that of 
        the requested attribute
        
        >>> n = Node('div')
        >>> n.p
        <wither.Node object at ...>
        """
        e_node = _etree.Element(tag)
        self._node.append(e_node)

        node = Node(e_node)

        return node
    
    def __enter__(self):
        """ 
        >>> with Node('body') as body:
        ...     pass
        """
        return self
        
    def __exit__(self, *tb):
        pass
        
    def __call__(self, **attribs):
        """ 
        >>> a = Node('a')(href='http://www.example.org')
        >>> a['href']
        'http://www.example.org'
        
        :param attrib: XML attributes specfied in the python keyword argument 
        :returns: returns itself for use in a 'with' block
        :rtype: Node
        """
        self.node_attrib.update(attribs)
        
        return self

    def __eq__(self, other):
        """ 
        >>> a = Node('a')
        >>> a == 'My Text'
        <wither.Node object at ...>
        >>> a.node_text
        'My Text'

        :returns: returns itself for use in a 'with' block
        :rtype: Node
        """
        self.node_text = other
        
        return self

    def __str__(self):
        """ 
        >>> a = Node('a')(href='http://www.example.org')
        >>> print(a)
        <a href="http://www.example.org"/>
        """
        return _etree.tostring(self._node, encoding='unicode')
    
    def __etree__(self):
        ## Tested in wither.etree() command
        return self._node

    def __len__(self):
        """ 
        >>> div = Node('div')
        >>> div.p
        <wither.Node object at ...>
        >>> div.p
        <wither.Node object at ...>
        >>> len(div)
        2

        :returns: returns the ammount of child nodes
        :rtype: Int
        """
        return len(self._node)
        
def etree(node):
    """Convert a Node to an etree object
    
    operations on the returned node will update the generated XML document
    
    to convert the etree object back to a node use :py:class:`Node` (etree)
    
    >>> n = Node('a')(href='http://www.example.org') == "RFC2606 domain"
    >>> etree(n)
    <Element a at ...>

    :param Node node: wither.Node object to convert to an etree.Element object
    :returns: etree Backing store for node
    :rtype: etree.Element
    """
    
    return node.__etree__()
