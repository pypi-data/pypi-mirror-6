from __future__ import absolute_import
from pyprotobuf.log import trace
from pyprotobuf.outputbuffer import OutputBuffer
from pyprotobuf.tokenizer import Identifier
from pyprotobuf.visitor import Visitor
import logging
import pyprotobuf.nodes as nodes


class ResolveError(Exception):
    def __init__(self, name, frame, message):
        super(ResolveError, self).__init__(message)
        self.name = name
        self.frame = frame

    def __str__(self):
        if isinstance(self.name, Identifier):
            pos = ' [%s:%s]\n' % (self.name.line,self.name.column)
        else:
            pos = ''

        string = ['ResolveError: ', self.message, '\n']
        string+= ['\t in ', str(self.frame.get_current_file().filename), pos]
        string+= ['\t scope', str(self.frame.package_scope[-1])]
        return ''.join(string)


class Frame(object):
    logger = logging.getLogger("pyprotobuf.Frame")
    logger.setLevel(logging.INFO)

    def __init__(self):
        # the current package name
        self.id_scope = ['']

        # the stack of nodes being operated on
        self.scope = []

        # all resolvable names inside the current package
        self.package_scope = [{}]

    def get_current_file(self):
        for node in reversed(self.scope):
            if isinstance(node, nodes.FileNode):
                return node

    def resolve_name(self, name):
        if isinstance(name, nodes.ParseNode):
            return name

        str_name = str(name)
        parts = str(name).split('.')

        # check single part name
        # start from the innermost scope and work up to the filenode until we find a match
        for node in reversed(self.scope):
            for child in node.children:
                if child.name == str_name:
                    return child

            if isinstance(node, nodes.FileNode):
                break

        # check the package scope for a fully qualified name
        if str_name in self.package_scope[-1]:
            return self.package_scope[-1][str_name]

        # check the package scope for a partial name
        if parts[0] in self.package_scope[-1]:
            node = self.package_scope[-1][parts[0]]
            return self._resolve(node, parts[1:])

        raise ResolveError(name, self, 'Cant resolve %s' % name)

    def _resolve(self, parent, parts):
        if not parts:
            return parent

        found = None
        name = parts[0]

        for child in parent.children:
            if child.name == name:
                found = child
                break

        if not found:
            raise ResolveError(name, self, 'Cant resolve %s' % name)

        return self._resolve(found, parts[1:])

    def add_to_package_scope(self, name, node):
        self.package_scope[-1][name] = node

    def push_package_scope(self):
        self.package_scope.append({})

    def pop_package_scope(self):
        return self.package_scope.pop()

    def push_id_scope(self, prefix):
        self.logger.debug('Push scope %s', prefix)
        self.id_scope.append(prefix)

    def pop_id_scope(self):
        self.logger.debug('Pop scope %s', self.id_scope.pop())




class FrameVisitor(Visitor):
    logger = logging.getLogger("pyprotobuf.FrameVisitor")
    logger.setLevel(logging.DEBUG)

    def __init__(self, frame=None):
        super(FrameVisitor, self).__init__()
        self.output = OutputBuffer()
        self.frame = frame or Frame()

    def trace(self, *args, **kwargs):
        trace(self.logger, *args, **kwargs)

    def visit_Package(self, package):
        """ Push the package name as the scope prefix.
        """
        self.frame.push_package_scope()

        if package.is_named():
            self.frame.push_id_scope(package.name)

        self.trace('Visiting package node %s', package.name)

        self.visit(package)

        if package.is_named():
            self.frame.pop_id_scope()

        self.frame.pop_package_scope()


    def visit(self, parent):
        children = getattr(parent, 'children', [])

        self.frame.scope.append(parent)

        for child in children:
            cls = child.__class__.__name__

            # if defined, call the named visit_* function in subclasses
            if hasattr(self, 'visit_%s' % cls):
                getattr(self, 'visit_%s' % cls)(child)
            else:
                self.visit_unknown(child)

            # recurse into the children
            if getattr(child, 'children', []):
                self.visit(child)

        self.frame.scope.pop()


class CodeGenerator(Visitor):
    logger = logging.getLogger("pyprotobuf.CodeGenerator")
    
    def __init__(self, frame=None):
        super(CodeGenerator, self).__init__()
        self.output = OutputBuffer()

    def generate_file(self, filenode):
        """ Generate  a FileNode.
        """
        raise NotImplementedError


    def visit(self, parent):
        children = getattr(parent, 'children', [])

        output = []

        for child in children:
            cls = child.__class__.__name__

            # if defined, call the named visit_* function in subclasses
            if hasattr(self, 'visit_%s' % cls):
                val = getattr(self, 'visit_%s' % cls)(child)
                output.append(val)
            else:
                self.visit_unknown(child)

            # recurse into the children
            if getattr(child, 'children', []):
                output.extend(self.visit(child))

        return output