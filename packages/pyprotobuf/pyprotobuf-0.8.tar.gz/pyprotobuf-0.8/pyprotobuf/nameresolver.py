from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import FrameVisitor
from pyprotobuf.compilerpass import CompilerPass


class NameResolver(CompilerPass):
    """ Link together ParseNodes when they refer to each other.
    """
    logger = logging.getLogger('pyprotobuf.NameResolver')

    def process(self, root):
        self.logger.debug('Resolving names...')
        visitor = self.Visitor()
        visitor.visit(root)

    class Visitor(FrameVisitor):
        logger = logging.getLogger('pyprotobuf.NameResolver.Visitor')
        logger.setLevel(logging.INFO)

        def add_children_to_package_scope(self, node, namespace=None):
            if namespace is None:
                namespace = []

            for child in node.children:
                namespace.append(str(child.name))

                if isinstance(child, nodes.EnumNode):
                    self.frame.add_to_package_scope('.'.join(namespace), child)
                    self.add_children_to_package_scope(child, namespace)
                elif isinstance(child, nodes.MessageNode):
                    self.frame.add_to_package_scope('.'.join(namespace), child)
                    self.add_children_to_package_scope(child, namespace)

                namespace.pop()

        def visit_ImportNode(self, node):
            if self.frame.id_scope[-1] == node.package.name:
                prefix = []
            else:
                prefix = [str(node.package.name)]

            self.add_children_to_package_scope(node.package.children[0], prefix)


        def visit_ExtendNode(self, node):
            node.message_node = self.frame.resolve_name(node.name)
            self._resolve_fields(node)

        def _resolve_fields(self, node):

            self.logger.debug('Visit message %s', node.name)

            frame = self.frame
            fields = node.get_children_of_type(nodes.FieldDescriptorNode)

            for field in fields:
                # only handle special types
                if str(field.type) in nodes.TYPES:
                    continue

                if field.type == node.name:
                    self.logger.info('Resolved self reference %s <- %s.%s' % (node.name, node.name, field.name))
                    field.type = node
                    continue

                # only evaluate non evaluated
                if not isinstance(field.type, nodes.ParseNode):
                    try:
                        # replace the field.type by searching the scopes
                        t = frame.resolve_name(field.type)
                        self.logger.info('Resolved %s -> %s %s', field.type, t.get_full_typename(), type(t))
                        field.type = t
                        field.add_dependency(field.type)
                    except Exception, e:
                        raise
                        #raise Exception("Undefined reference %s" % field.type)

                if hasattr(field, 'default'):
                    # enum nodes defaults are constrained to the enum
                    if isinstance(field.type, nodes.EnumNode):
                        # if the name is a member of the enum, use that
                        if field.type.has(field.default):
                            field.default_node = field.type.get(field.default)
                        else:
                            field.default_node = frame.resolve_name(field.default)
                    elif not field.default.isdigit():
                        # resolve the name (if its a name)
                        field.default_node = frame.resolve_name(field.default)
                    else:
                        field.default = field.default.strip("'\"")



        def visit_MessageNode(self, node):
            self.frame.scope.append(node)
            self._resolve_fields(node)
            self.frame.scope.pop()
            

