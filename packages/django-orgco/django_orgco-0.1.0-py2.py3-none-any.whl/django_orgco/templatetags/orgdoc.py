# -*- coding: utf-8 -*-
"""
django-orgco

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from orgco import convert_html

from django.template import Library, Node


register = Library()


@register.tag(name="orgdoc")
def do_orgco_convert_html(parser, token):
    args = token.contents.split()[1:]
    nodelist = parser.parse(('endorgdoc',))
    parser.delete_first_token()
    return OrgDocNode(nodelist, args)


class OrgDocNode(Node):

    def __init__(self, nodelist, args):
        self.nodelist = nodelist
        self.args = args

    def render(self, context):
        highlight = 'highlight' in self.args

        output = self.nodelist.render(context)
        output = convert_html(output, highlight=highlight)
        return output
