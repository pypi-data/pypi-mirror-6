from __future__ import absolute_import
import collections
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.tokenizer import Identifier
from pyprotobuf.codegenerator import CodeGenerator

logger = logging.getLogger('pyprotobuf.protorpc')

PROTORPC_TYPE_MAP = {
    'bool': 'messages.BooleanField',
    'bytes': 'messages.BytesField',
    'double': 'messages.FloatField',
    'enum': 'messages.EnumField',
    'fixed32': 'messages.IntegerField',
    'fixed64': 'messages.IntegerField',
    'float': 'messages.FloatField',
    'int32': 'messages.IntegerField',
    'int64': 'messages.IntegerField',
    'message': 'messages.MessageField',
    'sfixed32': 'messages.IntegerField',
    'sfixed64': 'messages.IntegerField',
    'sint32': 'messages.IntegerField',
    'sint64': 'messages.IntegerField',
    'string': 'messages.StringField',
    'uint32': 'messages.IntegerField',
    'uint64': 'messages.IntegerField'
}

IMPORTS = '''################################################################################
# Automatically generated. Do not modify this file                             #
################################################################################
# %s
'''


INDENT = '    '

class ProtoRPC(CodeGenerator):
    def __init__(self):
        super(ProtoRPC, self).__init__()
        self.imported_names = []

    def generate_file(self, protonode, **kwargs):
        self.header = kwargs.pop('header')
        if self.header:
            self.output.write(IMPORTS % protonode.filename + '\n')

        self.output.write('from protorpc import messages\n')

        output = self.visit(protonode)

        # write any extra imports
        for name in self.imported_names:
            module_name = '.'.join(name.split('.')[0:-1])
            self.output.write('import {}\n'.format(module_name))

        self.output.write("\n\n")

        self.output.write(''.join(output))

        # write the file
        return self.output.to_string()

    def visit_EnumNode(self, node, depth=0):

        if getattr(node, 'visited', False):
            return ''

        indent = INDENT * depth

        string = [indent]

        string.append('class %s(messages.Enum):\n' % node.name)

        enum_assignments = filter(lambda x: isinstance(x, nodes.EnumAssignmentNode), node.children)

        indent = INDENT * (depth + 1)
        for enum in enum_assignments:
            name, value = enum.name, enum.value
            string.append(indent)
            string.append("%s = %s\n" % (name, value))

        if not enum_assignments:
            string.append(indent)
            string.append("pass\n")


        string.append("\n")


        # mark as visited so we dont output twice
        # XXX: improve file node traversal so we dont need this
        # TODO: we should be able to remove this now that we have a dependency sorter pass
        setattr(node, 'visited', True)
        return ''.join(string)


    def visit_MessageNode(self, node, depth=0):
        if getattr(node, 'visited', False):
            return

        string = []
        enums = filter(lambda x: isinstance(x, nodes.EnumNode), node.children)
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        childmessages = filter(lambda x: isinstance(x, nodes.MessageNode), node.children)
        fields = sorted(fields, key=lambda x: x.number)
        indent = INDENT * depth

        string.append(indent)
        string.append('class %s(messages.Message):\n' % node.name)


        if node.comment:
            string.append(MultiLineComment(node.comment.value.split("\n")).serialize(depth+1)+'\n')

        lines = []

        for enum in enums:
            string.append(self.visit_EnumNode(enum, depth+1))


        if childmessages:
            string.append('\n')


            # output any children
            for child in childmessages:
                string.append(self.visit_MessageNode(child, depth + 1))

        # output fields or pass statement
        if fields:
            for field in fields:
                lines.append(self.output_field(node, field, depth))
            string.append('\n'.join(lines))
        else:
            indent = INDENT * (depth + 1)
            string.append(indent+'pass\n')

        string.append('\n\n\n')
        setattr(node, 'visited', True)
        return ''.join(string)


    def output_field(self, message, field, indent):
        is_message_field = False
        custom_field_type = False

        field_meta_type = PROTORPC_TYPE_MAP.get(str(field.type))
        field_meta_type_name = ''

        if isinstance(field.type, nodes.MessageNode):
            is_message_field = True
            field_meta_type_name = field.type.name
            field_meta_type =  'messages.MessageField'

            if field.type.has_option(Identifier('python_field_type')):
                custom_field_type = True
                field_meta_type = field.type.get_option(Identifier('python_field_type'))
                self.imported_names.append(field_meta_type )

        elif isinstance(field.type, nodes.EnumNode):
            is_message_field = True
            field_meta_type = PROTORPC_TYPE_MAP.get('enum')
            field_meta_type_name = field.type.name

        line = []


        if field.comment:
            line.append(MultiLineComment(field.comment.value.split("\n")).serialize(indent+1)+'\n')


        call = Call(field_meta_type)


        if is_message_field and not custom_field_type:
            call.add_argument(field_meta_type_name)

        call.add_argument(field.number)

        assignment = Assignment(field.name, call)


        if field.label == "required":
            call.add_keyword_argument('required', True)

        if field.label == "repeated":
            call.add_keyword_argument('repeated', True)

        if hasattr(field, 'default'):
            default_value = field.default

            # default_node is set if the the fields default value references a enum
            if hasattr(field, 'default_node'):
                enum_node = field.default_node

                # build a FQN up to this message node
                fqn = [enum_node.name]
                for parent in enum_node.get_parents():
                    if parent == message:
                        break
                    if parent.name is None:
                        break
                    fqn.append(parent.name)

                logger.debug('Generate enum %s', fqn)
                fqn = '.'.join(reversed(fqn))

                default_value = '%s' % fqn
            else:
                # handle boolean types
                if field.type == 'bool':
                    default_value = True if field.default == 'true' else False

                default_value = default_value

            if str(field.type) in ['string']:
                default_value = '"{}"'.format(default_value.encode('string-escape'))

            call.add_keyword_argument('default', default_value)

        line.append(assignment.serialize(indent+1))
        return ''.join(line)



class Node(object):
    def __str__(self):
        return self.serialize()

    def serialize(self, depth=None):
        raise NotImplementedError


class MultiLineComment(Node):
    def __init__(self, lines):
        self.lines = lines

    def serialize(self, depth=None):
        depth = depth or 0
        indent = INDENT * depth
        string = [indent, '""" ']

        for i, line in enumerate(self.lines):
            if i > 0:
                string.append(indent*2)

            string.append(line)

            if len(self.lines) > 1:
                string.append("\n")

        if len(self.lines) > 1:
            string.append(indent)
        else:
            string.append(" ")
        string.append('"""')
        return ''.join(string)



class Assignment(Node):
    name = None
    value = None
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def serialize(self, depth=None):
        depth = depth or 0
        indent = INDENT * depth
        string = [indent]
        string.append(' '.join([self.name, '=', str(self.value)]))
        return ''.join(string)



class ClassDefinition(Node):
    name = None

    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def serialize(self, depth=None):
        depth = depth or 0
        indent = INDENT * depth
        string = [indent]
        for child in self.children:
            string.append(child.serialize(depth+1))

        return '\n'.join(string)


class Call(Node):
    def __init__(self, name):
        self.name = name
        self.args = []
        self.kwargs = collections.OrderedDict()

    def add_argument(self, arg):
        self.args.append(arg)

    def add_keyword_argument(self, name, value):
        self.kwargs[name] = value

    def serialize(self, depth=None):
        string = [self.name, '(']


        arg_string = []
        for arg in self.args:
            arg_string.append(str(arg))

        for name, value in self.kwargs.iteritems():
            arg_string.append('{0}={1}'.format(name, value))

        string.append(', '.join(arg_string))
        string.append(')')
        return ''.join(string)



__generator__ = ProtoRPC
