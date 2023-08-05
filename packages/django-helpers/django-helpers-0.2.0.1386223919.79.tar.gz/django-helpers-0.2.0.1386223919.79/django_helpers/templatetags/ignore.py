# coding=utf-8
from django import template

register = template.Library()


class IgnoreNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        return ""


# noinspection PyUnusedLocal
@register.tag
def ignore(parser, token):
    node_list = parser.parse(('endignore',))
    return IgnoreNode()