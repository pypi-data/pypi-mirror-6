

class Types(object):
    BOOL = 'bool'
    STRING = 'string'
    INT32 = 'int32'
    INT64 = 'int64'
    UINT32 = 'uint32'
    UINT64 = 'uint64'
    SINT32 = 'sint32'
    SINT64 = 'sint64'
    FIXED32 = 'fixed32'
    FIXED64 = 'fixed64'
    SFIXED32 = 'sfixed32'
    SFIXED64 = 'sfixed64'
    DOUBLE = 'double'
    FLOAT = 'float'
    BYTES = 'bytes'
    ENUM = 'enum'
    MESSAGE = 'messsage'
    GROUP = 'group'

TYPES = [
    Types.BOOL,
    Types.STRING,
    Types.INT32,
    Types.INT64,
    Types.UINT32,
    Types.UINT64,
    Types.SINT32,
    Types.SINT64,
    Types.FIXED32,
    Types.FIXED64,
    Types.SFIXED32,
    Types.SFIXED64,
    Types.DOUBLE,
    Types.FLOAT,
    Types.BYTES,
    Types.ENUM,
    Types.MESSAGE,
    Types.GROUP
]

NUMERIC_TYPES = [
    Types.INT32,
    Types.INT64,
    Types.UINT32,
    Types.UINT64,
    Types.SINT32,
    Types.SINT64,
    Types.FIXED32,
    Types.FIXED64,
    Types.SFIXED32,
    Types.SFIXED64,
    Types.DOUBLE,
    Types.FLOAT
]



class ParseNode(object):
    children = None
    comment = None

    def __init__(self, parent=None):
        self.children = []
        self.parent = parent
        self.name = None
        self.type = None
        self.comment = None

        # dependencies used for topological sorting
        self.dependencies = set()

        # a map used to store options keys/values
        self.options = {}

    def get_file(self):
        for parent in self.get_parents():
            if isinstance(parent, FileNode):
                return parent

    def add_child(self, c):
        assert isinstance(c, ParseNode), "Child must be a ParseNode. Got %s" % type(c)
        self.children.append(c)
        c.parent = self

    def get_child(self, index):
        return self.children[index]

    def get_full_typename(self):
        fqn = [str(self.name) if self.name else '']
        parent = self.parent
        while parent is not None:
            if parent.name is not None:
                fqn.append(str(parent.name))
            parent = parent.parent

        return '.'.join(list(reversed(fqn)))

    def add_dependency(self, dep):
        """
            :param dep: ParseNode
        """
        self.dependencies.add(dep)
        for parent in self.get_parents():
            parent.add_dependency(dep)

    def get_dependencies(self):
        """
            :rtype: list[ParseNode]
        """
        return self.dependencies

    def get_parents(self):
        """
            :rtype: list[ParseNode]
        """
        parent = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent

    def get_full_name(self):
        assert self.name is not None, ("Name must not be none", self)
        fqn = [str(self.name)]
        parent = self.parent
        while parent is not None:
            if parent.name is not None:
                fqn.append(str(parent.name))
            parent = parent.parent

        return '.'.join(list(reversed(fqn)))

    def get_children_of_type(self, node_class):
        """
            :type node_class: T
            :rtype: list[V <= T]
        """
        return filter(lambda x: isinstance(x, node_class), self.children)

    def __repr__(self):
        if isinstance(self, CommentNode):
            return '#'
        return '%s("%s", %s)' % (
            self.__class__.__name__, self.name, self.children)#','.join([repr(f) for f in self.children]))

    @property
    def depth(self):
        depth = 0
        parent = self.parent
        while parent is not None:
            depth += 1
            parent = parent.parent
        return depth

    def resolve_name(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def has_option(self, name):
        return name in self.options

    def set_option(self, name, value):
        self.options[name] = value

    def get_option(self, *args):
        return self.options.get(*args)

    def to_proto(self):
        raise NotImplementedError

import pprint


class RootNode(ParseNode):
    def __repr__(self):
        return '%s(\n%r)' % (self.__class__.__name__, self.children)


class FileNode(ParseNode):
    filename = None

    def __repr__(self):
        return 'FileNode(filename="%s")' % self.filename

    def get_imports(self):
        return self.get_children_of_type(ImportNode)


class CommentNode(ParseNode):
    pass


class Package(ParseNode):
    name = None


    def is_named(self):
        return self.name is not None

    def __repr__(self):
        return '%s(%s,\n %s)' % (self.__class__.__name__, self.name, pprint.pformat(self.children))


class PackageDefinition(ParseNode):
    name = None

    def to_proto(self):
        return 'package %s;' % self.name

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.name)


class ServiceNode(ParseNode):
    name = None

    def to_proto(self):
        string = []
        for child in self.children:
            if isinstance(child, MessageNode):
                string.append(child.tostr(1))
            else:
                string.append(str(child))

        string = '\n'.join([('   ' + f) for f in string])
        return "service %s {\n%s\n%s}" % (self.name, string, '   ')


class MethodNode(ParseNode):
    name = None
    request_type = None
    response_type = None

    def __str__(self):
        return "rpc %s (%s) returns (%s);" % (self.name, self.request_type, self.response_type)


class MessageNode(ParseNode):
    name = None

    def tostr(self, depth):
        string = []
        for child in self.children:
            if isinstance(child, MessageNode):
                string.append(child.tostr(depth + 1))
            else:
                string.append(str(child))

        string = '\n'.join([('   ' * depth + f) for f in string])
        return "message %s {\n%s\n%s}" % (self.name, string, '   ' * (depth - 1))

    def to_proto(self):
        return self.tostr(1)


class FieldDescriptorNode(ParseNode):
    """
        Properties:
            label: One of "repeated", "optional" or "required".
            number: The tag/number/id of the field.
            name: The name of the field.
            type: Can be a string (Enum of proto types), MessageNode or EnumNode.
    """
    label = None
    number = None
    name = None
    type = None

    class LabelType(object):
        REPEATED = 'repeated'
        OPTIONAL = 'optional'
        REQUIRED = 'required'

    def __repr__(self):
        return 'FieldDescriptorNode(number="%s", name="%s", label="%s", type="%s")' % (self.number, self.name,
                                                                                    self.label, self.type)
    def to_proto(self):
        t = self.type
        if isinstance(self.type, MessageNode):
            t = self.type.name
        return '{0} {1} {2} = {3};'.format(self.label, t, self.name, self.number)


class EnumNode(ParseNode):
    name = None

    def __repr__(self):
        map = {}
        for c in self.children:
            map[str(c.name)] = str(c.value)

        return 'EnumNode("%s", %s)' % (self.name, map)

    def has(self, key):
        for c in self.children:
            if c.name == key:
                return True

        return False

    def get(self, key):
        for c in self.children:
            if c.name == key:
                return c

        return None

    def to_proto(self):
        return 'enum %s { %s }' % (self.name, ' '.join(map(str, self.children)) )


class EnumAssignmentNode(ParseNode):
    name = None
    value = None
    def to_proto(self):
        return '{0} = {1};'.format(self.name, self.value)


class OptionNode(ParseNode):
    name = None
    value = None
    def to_proto(self):
        return 'option {0} = {1};'.format(self.name, self.value)


class ExtendNode(ParseNode):
    name = None
    def __init__(self, parent=None):
        """
            :type message_node: MessageNode
        """
        super(ExtendNode, self).__init__(parent)

    @property
    def message_node(self):
        """
            :rtype: MessageNode
        """
        return self._message_node

    @message_node.setter
    def message_node(self, v):
        """
            :type v: MessageNode
        """
        self._message_node = v

    def to_proto(self):
        return 'extend %s { %s }' % (self.name, ' '.join(map(str, self.children)) )


class OptionalNode(ParseNode):
    def to_proto(self):
        return 'optional {0} {1} = {2};'.format(self.name, self.type, self.value)


class SyntaxNode(ParseNode):
    def to_proto(self):
        return 'syntax = "{0}";'.format(self.value)


class ImportNode(ParseNode):
    """ value: path
    """
    value = None

    def to_proto(self):
        return 'import "{0}";'.format(self.value)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.value)


class ExtensionsNode(ParseNode):
    def to_proto(self):
        return 'extension  {0} to {1};'.format(self.start, self.end)
