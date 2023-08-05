from pyprotobuf.codegenerator import FrameVisitor
from pyprotobuf.compilerpass import CompilerPass
import pyprotobuf.nodes as nodes
import logging

class FilePackager(CompilerPass):
    """
        Associate a package name with each FileNode.

        Search for PackageDefinition under the FileNode to define its package.
    """
    def process(self, root):
        visitor = self.Visitor()
        visitor.visit(root)

    class Visitor(FrameVisitor):
        logger = logging.getLogger('pyprotobuf.FilePackager.Visitor')
        logger.setLevel(logging.DEBUG)
        def visit_FileNode(self, node):
            for child in node.children:
                if isinstance(child, nodes.PackageDefinition):
                    node.package_name = child.name