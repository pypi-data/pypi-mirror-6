from __future__ import absolute_import
from pyprotobuf.codegenerator import FrameVisitor
from pyprotobuf.compilerpass import CompilerPass
import logging


class OptionResolver(CompilerPass):
    logger = logging.getLogger('pyprotobuf.OptionResolver')

    def process(self, root):
        visitor = self.Visitor()
        visitor.visit(root)

    class Visitor(FrameVisitor):
        logger = logging.getLogger('pyprotobuf.OptionResolver.Visitor')
        logger.setLevel(logging.DEBUG)
        def visit_OptionNode(self, node):
            self.frame.scope[-1].set_option(node.name, node.value)
            self.logger.debug('Set option %s = %s on %s', node.name, node.value, self.frame.scope[-1])
