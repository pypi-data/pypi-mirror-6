import logging

from tater.core.tokentype import Token
from tater.utils.itemstream import ItemStream
from tater.base.node import BaseNode
from tater.base.visitor import Visitor, IteratorVisitor


class Parser(object):
    '''Chains lexer, Node, and arbitrary visitors together.
    '''
    def __init__(self, *classes, **options):
        self.classes = classes
        self.options = options

    def __call__(self, input_, **options):
        _options = self.options
        _options.update(options)
        for cls in self.classes:
            if issubclass(cls, BaseNode):
                input_ = cls.parse(input_, **options)
            elif issubclass(cls, (Visitor, IteratorVisitor)):
                input_ = cls().visit(input_)
            else:
                input_ = cls(input_, **options)
        return input_
