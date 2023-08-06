#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2007, 2008, 2009, PediaPress GmbH
# See README.txt for additional licensing information.

try:
    from customconfig import css_map
except ImportError:
    css_map = {'rtl': 'direction:rtl;',
               'ltr': 'direction:ltr;',
               }
    

# The *css_map* is used to map node class to node styles
# Example:
# css_map = {
#     'control':'font-size: 110%;font-weight: bold;background-color:rgb(240, 240, 240);padding: 3px;margin-top: 1em;',
#     'doc_key': 'font-weight: bold; display: inline;', 
#     }

class CustomNodeTransformer(object):

    def __init__(self):
        pass

    def _updateStyles(self, node, styles):
        node_style = node.vlist.get('style', {})
        for style in styles.split(';'):
            try:
                style_name, style_val = style.split(':', 1)
            except ValueError:
                continue
            node_style[style_name.strip()] = style_val.strip()
        node.vlist['style'] = node_style

        
    def transformCSS(self, node):
        if getattr(node, 'vlist', None) == None:
            node_classes = []
        else:
            node_classes = node.vlist.get('class', '').split()

        for node_class in node_classes:
            if node_class in css_map:
                self._updateStyles(node, css_map[node_class])        
                
        for c in node.children:
            self.transformCSS(c)
