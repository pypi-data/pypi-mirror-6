"""
module for parsing dom-nodes or strings to an
object tree based on the classes in 'base.py'.

The ObjectParser instance takes an object
that provides 'mappings' via var(object):
names of tags are mapped to objects which
will be instantiated.

Currently only minidom is supported. 


"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.3 $'

from base import Element, Frag, Text

#
# Transformation from Dom to our Nodes
#
class ObjectParser:
    def __init__(self, spec):
        """ initialize ObjectParser with the Element tags
            contained in spec which are later used for
            tagname-to-Object parsing.
        """
        self.spec = spec
        self.typemap = {}
        for x,y in vars(spec).items():
            try:
                if issubclass(y, Element):
                    if hasattr(y, 'xmlname'):
                        x = y.xmlname
                    self.typemap[x]=y
            except TypeError:
                pass

    def parse(self, source):
        """ return xist-like objects parsed from UTF-8 string
            or dom tree.
            
            Fragment contains node objects and unknown a list of unmapped 
            nodes.
        """
        if type(source)==type(u''):
            source = source.encode('UTF8')

        if type(source)==type(''):
            from xml.dom import minidom
            tree = minidom.parseString(source)
        else:
            tree = source # try just using it as dom
        
        self.unknown_tags = []
        self.unknown_types = []
        res = self._dom2object(*tree.childNodes)
        return res

    def _dom2object(self, *nodes):
        """ transform dom-nodes to objects """
        res = Frag()

        for node in filter(None, nodes):
            if node.nodeType == node.ELEMENT_NODE:
                childs = self._dom2object(*node.childNodes)
                cls = self.typemap.get(node.nodeName)
                if not cls:
                    self.unknown_tags.append(node.nodeName)
                    res.extend(childs)
                else:
                    attrs = {}
                    if node.attributes:
                        for name, item in node.attributes.items():
                            attrs[name]=Text(item) # .nodeValue)
                    conv_node = cls(attrs, *childs)
                    res.append(conv_node)

            elif node.nodeType == node.TEXT_NODE:
                res.append(Text(node.nodeValue))
            else:
                self.unknown_types.append(node.nodeType)
        return res
