from pyprotobuf.compilerpass import CompilerPass
from pyprotobuf.codegenerator import FrameVisitor


class CommentResolver(CompilerPass):
    def process(self, root):
        visitor = self.Visitor()
        visitor.visit(root)

    class Visitor(FrameVisitor):
        """ associate comments with succeeding nodes

            an exception is made for the FileNode. The first comment in the file will apply to the FileNode
        """
        def __init__(self, frame=None):
            super(CommentResolver.Visitor, self).__init__(frame)
            self.last_comment = None
            self.current_file = None

        def visit_FileNode(self, child):
            self.current_file = child


        def visit(self, parent):
            for child in getattr(parent, 'children', []):
                cls = child.__class__.__name__
                if hasattr(self, 'visit_%s' % cls):
                    getattr(self, 'visit_%s' % cls)(child)
                else:
                    child.comment = self.last_comment
                    self.last_comment = None
                self.visit(child)

        def visit_CommentNode(self, child):
            if child.line == 0:
                self.current_file.comment = child
            else:
                self.last_comment = child


