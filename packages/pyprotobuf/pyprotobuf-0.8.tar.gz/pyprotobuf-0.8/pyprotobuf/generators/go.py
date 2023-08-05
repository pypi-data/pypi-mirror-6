"""

The proto package converts data structures to and from the
wire format of protocol buffers.  It works in concert with the
Go source code generated for .proto files by the protocol compiler.

A summary of the properties of the protocol buffer interface
for a protocol buffer variable v:

  - Names are turned from camel_case to CamelCase for export.
  - There are no methods on v to set fields; just treat
  	them as structure fields.
  - There are getters that return a field's value if set,
	and return the field's default value if unset.
	The getters work even if the receiver is a nil message.
  - The zero value for a struct is its correct initialization state.
	All desired fields must be set before marshaling.
  - A Reset() method will restore a protobuf struct to its zero state.
  - Non-repeated fields are pointers to the values; nil means unset.
	That is, optional or required field int32 f becomes F *int32.
  - Repeated fields are slices.
  - Helper functions are available to aid the setting of fields.
	Helpers for getting values are superseded by the
	GetFoo methods and their use is deprecated.
		msg.Foo = proto.String("hello") // set field
  - Constants are defined to hold the default values of all fields that
	have them.  They have the form Default_StructName_FieldName.
	Because the getter methods handle defaulted values,
	direct use of these constants should be rare.
  - Enums are given type names and maps from names to values.
	Enum values are prefixed with the enum's type name. Enum types have
	a String method, and a Enum method to assist in message construction.
  - Nested groups and enums have type names prefixed with the name of
  	the surrounding message type.
  - Extensions are given descriptor names that start with E_,
	followed by an underscore-delimited list of the nested messages
	that contain it (if any) followed by the CamelCased name of the
	extension field itself.  HasExtension, ClearExtension, GetExtension
	and SetExtension are functions for manipulating extensions.
  - Marshal and Unmarshal are functions to encode and decode the wire format.
"""
from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import CodeGenerator

logger = logging.getLogger('pyprotobuf.protorpc')

GO_TYPE_MAP = {
    'bool': 'bool',
    'bytes': 'byte',
    'double': 'messages.FloatField',
    #'enum': 'messages.EnumField',
    #'fixed32': 'messages.IntegerField',
    #'fixed64': 'messages.IntegerField',
    'float': 'fixed32',
    'int32': 'int32',
    'int64': 'int64',
    #'message': 'messages.MessageField',
    #'sfixed32': 'messages.IntegerField',
    #'sfixed64': 'messages.IntegerField',
    #'sint32': 'messages.IntegerField',
    #'sint64': 'messages.IntegerField',
    'string': 'string',
    'uint32': 'uint32',
    'uint64': 'uint64',
}
HEAD = """// Automatically generated
// Do not modify
// Source: %s
package
"""

PROLOG = """
import proto "code.google.com/p/goprotobuf/proto"
import json "encoding/json"
import math "math"

// Reference proto, json, and math imports to suppress error if they are not otherwise used.
var _ = proto.Marshal
var _ = &json.SyntaxError{}
var _ = math.Inf

"""


ENUM = """
var HatType_name = map[int32]string{
        1: "FEDORA",
        2: "FEZ",
}
var HatType_value = map[string]int32{
        "FEDORA": 1,
        "FEZ":    2,
}

func (x HatType) Enum() *HatType {
        p := new(HatType)
        *p = x
        return p
}
func (x HatType) String() string {
        return proto.EnumName(HatType_name, int32(x))
}
func (x HatType) MarshalJSON() ([]byte, error) {
        return json.Marshal(x.String())
}
func (x *HatType) UnmarshalJSON(data []byte) error {
        value, err := proto.UnmarshalJSONEnum(HatType_value, data, "HatType")
        if err != nil {
                return err
        }
        *x = HatType(value)
        return nil
}
"""

ENUM_BODY = """
func (x {name}) Enum() *{name} {{
        p := new({name})
        *p = x
        return p
}}
func (x {name}) String() string {{
        return proto.EnumName({name}_name, int32(x))
}}
func (x {name}) MarshalJSON() ([]byte, error) {{
        return json.Marshal(x.String())
}}
func (x *{name}) UnmarshalJSON(data []byte) error {{
        value, err := proto.UnmarshalJSONEnum({name}_value, data, "{name}")
        if err != nil {{
                return err
        }}
        *x = {name}(value)
        return nil
}}"""

FIELD_GETTER = """\
func (this *{0}) Get{1}() int32 {{
	if this != nil && this.{1} != nil {{
		return *this.{1}
	}}
	return 0
}}
"""


MESSAGE = """

// This is a message that might be sent somewhere.
type Request struct {
	Key []int64 `protobuf:"varint,1,rep,name=key" json:"key,omitempty"`
	//  optional imp.ImportedMessage imported_message = 2;
	Hue *Request_Color `protobuf:"varint,3,opt,name=hue,enum=my.test.Request_Color" json:"hue,omitempty"`
	Hat *HatType       `protobuf:"varint,4,opt,name=hat,enum=my.test.HatType,def=1" json:"hat,omitempty"`
	//  optional imp.ImportedMessage.Owner owner = 6;
	Deadline         *float32           `protobuf:"fixed32,7,opt,name=deadline,def=inf" json:"deadline,omitempty"`
	Somegroup        *Request_SomeGroup `protobuf:"group,8,opt,name=SomeGroup" json:"somegroup,omitempty"`
	Reset_           *int32             `protobuf:"varint,12,opt,name=reset" json:"reset,omitempty"`
	XXX_unrecognized []byte             `json:"-"`
}

func (m *Request) Reset()         { *m = Request{} }
func (m *Request) String() string { return proto.CompactTextString(m) }
func (*Request) ProtoMessage()    {}

const Default_Request_Hat HatType = HatType_FEDORA

var Default_Request_Deadline float32 = float32(math.Inf(1))

func (m *Request) GetKey() []int64 {
	if m != nil {
		return m.Key
	}
	return nil
}

func (m *Request) GetHue() Request_Color {
	if m != nil && m.Hue != nil {
		return *m.Hue
	}
	return Request_RED
}

func (m *Request) GetHat() HatType {
	if m != nil && m.Hat != nil {
		return *m.Hat
	}
	return Default_Request_Hat
}

func (m *Request) GetDeadline() float32 {
	if m != nil && m.Deadline != nil {
		return *m.Deadline
	}
	return Default_Request_Deadline
}

func (m *Request) GetSomegroup() *Request_SomeGroup {
	if m != nil {
		return m.Somegroup
	}
	return nil
}

func (m *Request) GetReset_() int32 {
	if m != nil && m.Reset_ != nil {
		return *m.Reset_
	}
	return 0
}
"""


def go_name_enum(node):
    # get the parents

    parent = node.parent
    name = [str(node.name)]
    while parent is not None:
        # stop at the package level
        if isinstance(parent, nodes.FileNode):
            break

        name.append(str(parent.name))

        parent = parent.parent


    # translate a node name to go
    return '_'.join(reversed(name))


def go_name_field(node):
    return camel_case(node.name)

def go_name(node):
    # translate a node name to go
    return camel_case(node.name)

def go_name_package(name):
    return str(name).replace('.', '_')

# key_that_needs_1234camel_CasIng
# GetKeyThatNeeds_1234Camel_CasIng

# http://www.ajanicij.info/content/protocol-buffers-go




def build_field_descriptor(field):
    protobuf_options = []

    if isinstance(field.type, (nodes.MessageNode)):
        protobuf_options.append('bytes')
    else:
        protobuf_options.append('varint')

    if field.label == 'repeated':
        protobuf_options.append('rep')

    protobuf_options.append(str(field.number))
    protobuf_options.append('name=%s' % str(field.name))
    
    #if field.type == enum
    #protobuf_options.append('enum=%s' % go_name(field.type))
    
    json_options = [field.name, 'omitempty']
    
    return '`protobuf:"%s" json:"%s"`' % (','.join(protobuf_options), ','.join(json_options))

def get_keys_max_len(keys):
    # round up to the nearest even
    max_len = max(map(len, keys))
    return max_len

class Go(CodeGenerator):
    comment = '#'

    def generate_file(self, protonode, **kwargs):
        if kwargs.get('header'):
            self.output.write(HEAD % (protonode.filename) + '\n\n')

        if protonode.package_name:
            self.output.write('package %s\n' % go_name_package(protonode.package_name))
        #print 'WRITE PROTO', protonode.package_name
        self.output.write(PROLOG)
        self.visit(protonode)
        return self.output.to_string()

    def visit_EnumNode(self, node):

        if getattr(node, 'visited', False):
            return


        enum_assignments = filter(lambda x: isinstance(x, nodes.EnumAssignmentNode), node.children)

        # output the type declaration

        enum_name = go_name_enum(node)

        self.output.write('type %s int32\n\n' % enum_name)

        import collections
        enum = collections.OrderedDict()

        keys = []




        # output the const declaration
        self.output.write('const (\n')

        const_assigns = collections.OrderedDict()
        for enum in enum_assignments:
            const_assigns['{}_{}'.format(enum_name, enum.name)] = enum.value

        max_key_len = get_keys_max_len(const_assigns.keys())
        format_string = '        {:<%s} {} = {}\n' % max_key_len

        for key,value in const_assigns.iteritems():
            self.output.write(format_string.format(key, enum_name, value))

        self.output.write(')\n\n')


        mapping_assigns = collections.OrderedDict()
        # output the name/value mappings
        self.output.write('var %s_name = map[int32]string{\n' % enum_name)
        for enum in enum_assignments:
            key = '{}:'.format(enum.value)
            if key in mapping_assigns:
                # TOOD: mark duplicates
                continue
            mapping_assigns[key] = '"{}"'.format(enum.name)
        self.output_mapping(mapping_assigns)
        self.output.write('}\n')


        mapping_assigns = collections.OrderedDict()
        self.output.write('var %s_value = map[string]int32{\n' % enum_name)
        for enum in enum_assignments:
            name, value = enum.name, enum.value
            key_marker = '"{}":'.format(name)
            mapping_assigns[key_marker ] = enum.value
        self.output_mapping(mapping_assigns)
        self.output.write('}\n')


        self.output.write(ENUM_BODY.format(name=go_name_enum(node)))
        self.output.write('\n\n')

        # mark as visited so we dont output twice
        # XXX: improve file node traversal so we dont need this
        setattr(node, 'visited', True)

    def output_mapping(self, kvs):
        max_key_len = get_keys_max_len(kvs.keys())
        format_string =  '        {:'+str(max_key_len)+'} {},\n'

        for key,value in kvs.iteritems():
            self.output.write(format_string.format(key, value))



    def visit_MessageNode(self, node):
        # loop over fields
        if getattr(node, 'visited', False):
            return

        enums = filter(lambda x: isinstance(x, nodes.EnumNode), node.children)
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        childmessages = filter(lambda x: isinstance(x, nodes.MessageNode), node.children)
        fields = sorted(fields, key=lambda x: x.number)

        if node.comment:
            self.output.write("// %s \n" % ( node.comment.value))

        for enum in enums:
            self.visit_EnumNode(enum)


        if childmessages:
            self.output.write('\n')

        for childmessage in childmessages:
            self.visit_MessageNode(childmessage)

        message_type_name = go_name_enum(node)

        self.output.write("type {0} struct {{\n".format(message_type_name))

        for field in fields:
            if field.type == 'group':
                # groups are deprecated
                continue

            if isinstance(field.type, nodes.EnumNode):
                field_type = go_name_enum(field.type)
            elif isinstance(field.type, nodes.MessageNode):
                field_type = go_name_enum(field.type)
            else:
                field_type = GO_TYPE_MAP.get(str(field.type))

            if field_type is None:
                raise Exception("unknown field type %s" % field.type)

            if field.label == "repeated":
                field_type = '[]' + field_type
            else:
                field_type = '*' + field_type


            self.output.write('        {0}\t{1}  {2}\n'.format(go_name_field(field), field_type,
                                                             build_field_descriptor(field)))

        self.output.write("}\n\n")


        # write getters
        for field in fields:
            self.output.write(FIELD_GETTER.format(message_type_name, go_name_field(field)))

        #self.output.write('\n\n')
        setattr(node, 'visited', True)

    def visit_FieldDescriptorNode(self, node):
        pass


"""
38	+	func TestCamelCase(t *testing.T) {
39	+		tests := []struct {
40	+			in, want string
41	+		}{
42	+			{"one", "One"},
43	+			{"one_two", "OneTwo"},
44	+			{"_my_field_name_2", "XMyFieldName_2"},
45	+			{"Something_Capped", "Something_Capped"},
46	+			{"my_Name", "My_Name"},
47	+			{"OneTwo", "OneTwo"},
48	+			{"_", "X"},
49	+			{"_a_", "XA_"},
50	+		}
51	+		for _, tc := range tests {
52	+			if got := CamelCase(tc.in); got != tc.want {
53	+				t.Errorf("CamelCase(%q) = %q, want %q", tc.in, got, tc.want)
54	+			}
55	+		}
56	+	}"""


def camel_case(string):
    """

    ported from https://code.google.com/p/goprotobuf/source/browse/protoc-gen-go/generator/generator.go

    """
    if not string:
        return

    name = []
    i = 0

    if string[0] == '_':
        # Need a capital letter; drop the '_'.
        name.append('X')
        i += 1


    len_string = len(string)
    # Invariant: if the next letter is lower case, it must be converted
    # to upper case.
    # That is, we process a word at a time, where words are marked by _ or
    # upper case letter. Digits are treated as words.
    while i < len_string:
        c = string[i]
        if c == '_' and i+1 < len_string and string[i+1].islower():
            # // Skip the underscore in s.
            i += 1
            continue

        if c.isdigit():
            name.append(c)
            i += 1
            continue

        # Assume we have a letter now - if not, it's a bogus identifier.
        # The next word is a sequence of characters that must start upper case.
        if c.islower():
            c = c.upper()

        # Guaranteed not lower case.
        name.append(c)

        # Accept lower case sequence that follows.
        while i+1 < len_string and string[i+1].islower():
            i += 1
            name.append(string[i])
        i += 1

    return ''.join(name)


__generator__ = Go
