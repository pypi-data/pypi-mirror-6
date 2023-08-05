from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import FrameVisitor
from pyprotobuf.compilerpass import CompilerPass


class ExtensionsResolver(CompilerPass):
    """ Link together ParseNodes when they refer to each other.
    """
    logger = logging.getLogger('pyprotobuf.ExtensionResolver')

    def process(self, root):
        self.logger.debug('Resolving names...')
        visitor = self.Visitor()
        visitor.visit(root)

    class Visitor(FrameVisitor):
        logger = logging.getLogger('pyprotobuf.ExtensionResolver.Visitor')
        logger.setLevel(logging.INFO)

        def visit_ExtendNode(self, node):
            """
                :type node: nodes.ExtendNode
            """
            message_node = node.message_node
            extensions = message_node.get_children_of_type(nodes.ExtensionsNode)

            # quick hack to check extension space
            ranges = []
            for extension in extensions:
                ranges += range(extension.start, extension.end)

            self.logger.debug('Extending %s %s', message_node, node)
            # create a new
            for field in node.get_children_of_type(nodes.FieldDescriptorNode):
                message_node.add_child(field)

                if isinstance(field.type, nodes.MessageNode):
                    message_node.add_dependency(field.type)
