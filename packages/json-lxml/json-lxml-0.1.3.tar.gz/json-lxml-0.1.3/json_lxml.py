# -*- coding: utf-8 -*-
"""convert between python value and lxml.etree so that lxml's power can be applied to json data.
In particular, xpath queries can be run against json.
"""
import types
from lxml import etree

type_map=dict(
    int=int,
    unicode=unicode,
    NoneType=lambda x: None,
    list=list,
    bool=bool,
    str=str,
    )

def element(k, v):
    """ key, val --> etree.Element(key)
    """

    node=etree.Element(k)

    if isinstance(v, dict):
        for ck,cv in v.items():
            node.append(element(ck, cv))
    elif isinstance(v, (int,float,bool,basestring,types.NoneType)): # scalar
        node.set('type', type(v).__name__)
        node.text=str(v)
    elif isinstance(v, list):
        node.set('type', type(v).__name__) # list xx this could be done across the board.
        for i,cv in enumerate(v):
            node.append(element("_list_element_%d" % i, cv))
    else:
        assert False, type(v)

    return node

def value(e):
    """ etree.Element --> value
    """

    children=e.getchildren()

    typ=e.get('type')
    if children:
        if not typ:             # xx defaults dict
            return dict( (c.tag.decode('utf8'), value(c)) for c in children )
        elif typ=='list':
            return [ value(c) for c in children ]
        else:
            raise TypeError('unexpected type', typ)

    # convert it back to the right python type
    ctor=type_map[typ]
    return ctor(e.text)

def xpath(val, xpath):

    for node in element('root', val).xpath(xpath):
        yield value(node)

