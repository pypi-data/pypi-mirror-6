import os
from pyprotobuf.filepackager import FilePackager
from pyprotobuf.parser import ProtoParser, ParseError
from pyprotobuf.nameresolver import NameResolver
from pyprotobuf.commentresolver import CommentResolver
from pyprotobuf.optionresolver import OptionResolver
from pyprotobuf.dependencysorter import DependencySorter
from pyprotobuf.extensionsresolver import ExtensionsResolver
import pyprotobuf.nodes as nodes
import logging
import copy


logger = logging.getLogger('pyprotobuf.Compiler')


class Compiler(object):
    logger = logging.getLogger('pyprotobuf.Compiler')

    passes = [
        FilePackager,
        OptionResolver,
        NameResolver,
        ExtensionsResolver,
        DependencySorter,
        CommentResolver
    ]

    def __init__(self, generator_class):
        self.parser = ProtoParser()
        self.generator_class = generator_class
        self.import_paths = [os.getcwd(), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto')]
        self.generate_header = False

        self.imports = {}
        self.log_level = logging.INFO


    def set_log_level(self, log_level):
        self.log_level = log_level

    def set_import_paths(self, paths):
        self.import_paths = paths

    def compile(self, filename):
        with open(filename, 'r') as f:
            return self.compile_string(filename, f.read())

    def compile_string(self, filename, string):
        try:
            rootnode = self.precompile_string(filename, string)
        except ParseError as e:
            print str(e)
            raise

        generator = self.generator_class()
        # only compile the last package for now
        return generator.generate_file(rootnode.children[-1].children[0], header=self.generate_header)

    def precompile_string(self, filename, string):
        self.packages = nodes.RootNode()
        self.traversal_path = []

        filename = os.path.abspath(filename)

        package = self.parser.parse_string(string)
        # so the generators know the path 
        package.children[0].filename = filename

        filedir = os.path.dirname(filename)

        if filedir not in self.import_paths:
            self.import_paths.insert(0, filedir)

        # resolve an add other packages before adding ours
        self.resolve_imports(package.children[0])

        self.packages.add_child(package)

        for compiler_pass_class in self.passes:
            compiler_pass = compiler_pass_class(self)
            compiler_pass.set_log_level(self.log_level)
            compiler_pass.process(self.packages)

        return self.packages


    def resolve_import_path(self, path, file_node=None):
        if path.startswith('/'):
            return path

        # search through each of the paths
        # if specified, starting relative to the directory of the package
        import_paths = copy.copy(self.import_paths)
        if file_node is not None:
            assert isinstance(file_node, nodes.FileNode)
            import_paths.insert(0, os.path.dirname(file_node.filename))

        split_path = path.split(os.pathsep)
        for import_path in import_paths:
            test_path = os.path.join(import_path, *split_path)
            if os.path.exists(test_path):
                return test_path

        raise Exception("Could not find import %s in paths %s" % (path, import_paths))


    def resolve_imports(self, file_node):
        """
        :param file_node: pyprotobuf.nodes.FileNode
        """
        assert isinstance(file_node, nodes.FileNode)


        # find any import nodes
        for child in file_node.get_imports():
            path = self.resolve_import_path(child.value, file_node)

            if path in self.imports:
                importnode = self.imports[path]
            else:
                importnode = self.import_package(path)
                self.logger.info('Importing %s from %s', path, file_node.filename)
                self.imports[path] = importnode

            child.package = importnode

            if path in self.traversal_path:
                self.traversal_path.append(path)
                raise Exception("Circular import %s" % self.traversal_path)

            # visit other imports before we add ours
            self.traversal_path.append(path)
            self.resolve_imports(importnode.children[0])
            self.traversal_path.pop()
            self.packages.add_child(importnode)

    def import_package(self, filename):
        """ Return the package node at path. 
        """
        if filename in self.traversal_path:
            raise Exception("Circular import %s from %s" % (filename, self.traversal_path))

        self.traversal_path.append(filename)

        with open(filename, 'r') as f:
            string = f.read()

        package = self.parser.parse_string(string)
        package.children[0].filename = filename

        self.resolve_imports(package.children[0])

        self.traversal_path.pop()

        return package
            
            