
class CompilerPass(object):
    def __init__(self, compiler):
        self.compiler = compiler

    def set_log_level(self, level):
        pass

    def process(self, root):
        """
        Subclasses should override this to process the AST.
        :param root: pyprotobuf.nodes.RootNode
        """
        raise NotImplementedError