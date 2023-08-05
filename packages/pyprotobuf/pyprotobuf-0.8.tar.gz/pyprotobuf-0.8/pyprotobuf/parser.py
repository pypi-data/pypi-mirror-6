from pyprotobuf.tokenizer import Tokenizer
from pyprotobuf.nodes import *

TOKEN_INDENT = 5
TOKEN_DEDENT = 6
TOKEN_SLASH = 17
TOKEN_VBAR = 18
TOKEN_AMPER = 19
TOKEN_LESS = 20
TOKEN_GREATER = 21
TOKEN_EQUAL = 22
TOKEN_DOT = 23
TOKEN_PERCENT = 24
TOKEN_BACKQUOTE = 25
TOKEN_EQEQUAL = 28
TOKEN_NOTEQUAL = 29
TOKEN_LESSEQUAL = 30
TOKEN_GREATEREQUAL = 31
TOKEN_TILDE = 32
TOKEN_CIRCUMFLEX = 33
TOKEN_LEFTSHIFT = 34
TOKEN_RIGHTSHIFT = 35
TOKEN_DOUBLESTAR = 36
TOKEN_PLUSEQUAL = 37
TOKEN_MINEQUAL = 38
TOKEN_STAREQUAL = 39
TOKEN_SLASHEQUAL = 40
TOKEN_PERCENTEQUAL = 41
TOKEN_AMPEREQUAL = 42
TOKEN_VBAREQUAL = 43
TOKEN_CIRCUMFLEXEQUAL = 44
TOKEN_LEFTSHIFTEQUAL = 45
TOKEN_RIGHTSHIFTEQUAL = 46
TOKEN_DOUBLESTAREQUAL = 47
TOKEN_DOUBLESLASH = 48
TOKEN_DOUBLESLASHEQUAL = 49

TOKEN_ERRORTOKEN = 52
TOKEN_N_TOKENS = 53
TOKEN_NT_OFFSET = 256

TOKEN_LBRACE = 26
TOKEN_RBRACE = 27
TOKEN_AT = 50
TOKEN_OP = 51
TOKEN_COLON = 11
TOKEN_COMMA = 12
TOKEN_LPAR = 7
TOKEN_RPAR = 8
TOKEN_LSQB = 9
TOKEN_RSQB = 10
TOKEN_PLUS = 14
TOKEN_MINUS = 15
TOKEN_STAR = 16
TOKEN_ENDMARKER = 0
TOKEN_NAME = 1
TOKEN_NUMBER = 2
TOKEN_STRING = 3
TOKEN_NEWLINE = 4
TOKEN_SPACE = 54
TOKEN_NL = 55
TOKEN_COMMENT = 55
TOKEN_SEMI = 13

import re
import logging

logger = logging.getLogger('pyprotobuf.parser')


scanner = re.Scanner([
    (r"[a-zA-Z_][\.\w]*", lambda scanner, token: (TOKEN_NAME, token)),
    (r"//.*", lambda scanner, token: (TOKEN_COMMENT, token[2:])),
    (r"\+|\-|\\|\*|\=|\{|\}", lambda scanner, token: (TOKEN_OP, token)),
    (r"(?:0x)?[0-9]+(\.[0-9]+)?", lambda scanner, token: (TOKEN_NUMBER, token)),
    (r";", lambda scanner, token: (TOKEN_SEMI, token)),
    (r"[\t ]+", lambda scanner, token: (TOKEN_SPACE, token)),
    (r'"(?:(?:\\.)|(?:[^"]))*"', lambda scanner, token: (TOKEN_STRING, token)),
    (r"\n", lambda scanner, token: (TOKEN_NL, token)),
])


class ParseError(Exception):
    def __str__(self):
        return 'Parse Error: %s [%s:%s]' % (self.message, self.line, self.col)


class ProtoParser(object):
    """ Parses a single proto file to an AST.
    """

    def __init__(self):
        pass

    def parse_string(self, s):
        """ proto =( message | extend | enum | import | package | option | ';' ) ;
        """
        tokenizer = Tokenizer(s)

        # the root is an anonymous package node
        self.root = Package()

        self.protonode = FileNode()

        self.root.add_child(self.protonode)

        while tokenizer.has_next():
            token = tokenizer.next_token()
            if self.check_single_line_comment(token):
                self.protonode.add_child(self.read_single_line_comment(tokenizer))
            elif self.check_multiline_line_comment(tokenizer, token):
                self.protonode.add_child(self.read_multi_line_comment(tokenizer))
            if token.type == TOKEN_NAME:
                self.protonode.add_child(self.parse_toplevel(tokenizer, token))

        return self.root

    def parse_toplevel(self, tokenizer, token):
        methods = {
            'package': self.parse_package_stmt,
            'message': self.parse_message_stmt,
            'import': self.parse_import_stmt,
            'enum': self.parse_enum_stmt,
            'option': self.parse_option_stmt,
            'extend': self.parse_extend_stmt,
            'syntax': self.parse_syntax_stmt,
            'service': self.parse_service_stmt
        }
        method = methods.get(token.value, None)

        logger.debug('Parse top-level: %s', token.value)

        if method is None:
            raise Exception("Unknown toplevel token %s" % token)

        node = method(tokenizer)
        return node

    def check_names(self, token, names):
        # TODO: varargs
        return token.type == TOKEN_NAME and token.value in names

    def check_single_line_comment(self, current_token):
        return current_token.type == TOKEN_OP and current_token.value == '//'

    def check_multiline_line_comment(self, t, current_token):
        return current_token.type == TOKEN_OP and current_token.value == '/' and t.readahead().value == '*'

    def read_single_line_comment(self, t):
        comment = []
        node = CommentNode()
        node.line, node.column = t.line, t.column

        while t.has_next():
            token = t.next_token(False)
            if token.value == "\n":
                t.line += 1
                break
            comment.append(token.value)
        logger.debug('Read comment %s', ' '.join(comment))

        node.value = ' '.join(comment)
        return node

    def read_multi_line_comment(self, t):
        node = CommentNode()
        node.line = t.line
        node.column = t.column

        star = t.next_token()
        assert star.value == '*'
        comment = []
        i = 0
        while t.has_next():

            token = t.next_token(skipnl=False)

            if i > 0 and token.value != '\n':
                comment.append(' ')

            i += 1

            if token.value == "\n":
                i = 0
                t.line += 1

            if token.value == '*' and t.readahead().value == '/':
                slash = t.next_token()
                assert slash.value == '/'
                break

            comment.append(token.value)

        logger.debug('Read comment %s', '\n'.join(comment))

        node.value = ''.join(comment)
        return node

    def read_name(self, t):
        return t.read_name()

    def read_dotted(self, t):
        tok = t.next_token()
        while t.has_next():
            more = t.readahead()
            if more.value != '.':
                break
            t.next_token()
            tok.value = tok.value + '.' + self.read_dotted(t).value
        return tok

    def read_string_or_id(self, t):
        tok = t.next_token()
        self.assert_token_expression(tok.type == TOKEN_STRING or tok.type == TOKEN_NAME, tok, "Expected ident/string literal. Got %s" % tok)
        if tok.type == TOKEN_STRING:
            tok.value = tok.value.strip("'" + '"')
        return tok

    def read_string_or_id_or_num(self, t):
        tok = t.next_token()
        self.assert_token_expression(tok.type == TOKEN_STRING or tok.type == TOKEN_NAME or tok.type == TOKEN_NUMBER, tok, "Expected ident/string literal/num. Got %s" % tok)
        if tok.type == TOKEN_STRING:
            tok.value = tok.value.strip("'" + '"')
        return tok

    def read_string(self, t):
        tok = t.next_token()
        self.assert_token_expression(tok.type == TOKEN_STRING, tok, "Expected string literal. Got %s" % tok)
        if tok.type == TOKEN_STRING:
            tok.value = tok.value.strip("'" + '"')
        return tok

    def read_string_or_dotted(self, t):
        tok = t.readahead()
        if tok.type == TOKEN_STRING and tok.value[0] in ['"', "'"]:
            tok.value = tok.value.strip("'" + '"')
            t.next_token()
            return tok
        return self.read_dotted(t)

    def read_equals(self, t):
        tok = t.next_token()
        self.assert_token_expression(tok.value == '=', tok, "Expected =, Got %s" % tok)
        return tok

    def read_number(self, t):
        tok = t.next_token()
        self.assert_token_expression(tok.type == TOKEN_STRING or tok.type == TOKEN_NUMBER, tok, "Expect Number. Got: %s" % tok)
        return tok

    def read_name2(self, t):
        tok = t.next_token()
        name = tok.value
        self.assert_token(name, TOKEN_NAME, message="Expected identifier. Got: %s" % name)
        return name

    def assert_token_expression(self, expr, token, error_message):
        if not expr:
            self.raise_token_error(token, error_message)

    def read_semi(self, t):
        semi = t.next_token(False)
        self.assert_token(semi, TOKEN_OP, value=";", message='Expected ; Got' + str(semi.value))

        # read any possible comments after a semi
        token = t.readahead()
        if token.type == TOKEN_OP and token.value == '//':
            node = self.read_single_line_comment(t)

    def assert_read(self, t, match_type, expected):
        next = t.next_token()
        self.assert_token(next, match_type, value=expected, message='Expected %s. Got %s' % (expected, next))

    def format_token_position(self, token):
        return "[%s:%s]" % (token.start[0], token.start[1])

    def raise_token_error(self, token, message):
        pe = ParseError(message)
        pe.line = token.start[0]
        pe.col = token.start[1]
        raise pe

    def assert_token(self, token, type, value=None, message=None):
        message = "Expected %s %s" % (value, self.format_token_position(token))

        pe = ParseError(message)
        pe.line = token.start[0]
        pe.col = token.start[1]

        if value is None:
            if token.type != type:
                raise pe
        else:
            if token.type != type and token.value != value:
                raise pe


    def parse_service_stmt(self, t):
        """
            service_defs = (option	 | method_def  | ';')+ ;
            service = 'service' ident '{' service_defs? '}' ;
        """
        node = ServiceNode()
        node.name = self.read_name(t)

        self.assert_read(t, TOKEN_OP, '{')

        while t.has_next():
            token = t.next_token()
            if self.check_names(token, ["option"]):
                node.add_child(self.parse_option_stmt(t))

            elif self.check_names(token, ["rpc"]):
                node.add_child(self.parse_method_def(t))

            elif self.check_single_line_comment(token):
                node.add_child(self.read_single_line_comment(t))
            elif self.check_multiline_line_comment(t, token):
                self.protonode.add_child(self.read_multi_line_comment(t))
            elif token.type == TOKEN_OP and token.value == '}':
                break

        return node

    def parse_method_def(self, t):
        """ method_options = '{' (option | ';')+ '}' ;
            method_def = 'rpc' ident '(' qualified_name ')' 'returns' '(' qualified_name ')' (method_options | ';') ;
        """
        node = MethodNode()
        node.name = self.read_name(t)
        self.assert_read(t, TOKEN_OP, '(')
        node.request_type = self.read_name(t)
        self.assert_read(t, TOKEN_OP, ')')
        self.assert_read(t, TOKEN_NAME, 'returns')
        self.assert_read(t, TOKEN_OP, '(')
        node.response_type = self.read_name(t)
        self.assert_read(t, TOKEN_OP, ')')
        return node

    def parse_option_stmt(self, t):
        """
            option = 'option' optionBody ';';
            optionBody = ident ( '.' ident )* '=' constant;

            # XXX: what are the parens for: "option (key) = value;" ?
        """
        node = OptionNode()

        token = t.readahead()

        has_open_paren = False
        if token.type == TOKEN_OP and token.value == '(':
            has_open_paren = True
            open_paren = t.next_token()

        node.name = self.read_name(t)

        if has_open_paren:
            self.assert_read(t, TOKEN_RPAR, ')')

        self.read_equals(t)
        node.value = self.read_string_or_id(t).value
        self.read_semi(t)

        logger.debug('Read option %s', node)
        return node

    def parse_message_stmt(self, t):
        """
            message ='message' ident messageBody;
            messageBody ='{' ( field | enum | message | extend | extensions | group | option | ':' )* '}';
        """
        message_name = self.read_name(t)

        self.assert_read(t, TOKEN_OP, '{')

        mnode = MessageNode()
        mnode.name = message_name
        logger.debug('Read message node %s', message_name)
        while t.has_next():
            token = t.next_token()
            if self.check_names(token, ['optional', 'repeated', 'required']):
                #logger.debug('Read field %s', message_name)
                # allow parse_field_desc to read the field label
                t.backtrack()
                node = self.parse_field_desc(t)
                node.parent = mnode
                mnode.add_child(node)
            elif self.check_names(token, ['option']):
                node = self.parse_option_stmt(t)
                node.parent = mnode
                mnode.add_child(node)
            elif self.check_single_line_comment(token):
                node = self.read_single_line_comment(t)
                mnode.add_child(node)
            elif self.check_multiline_line_comment(t, token):
                self.protonode.add_child(self.read_multi_line_comment(t))
            elif self.check_names(token, ['extensions']):
                node = self.parse_extensions_stmt(t)
                mnode.add_child(node)

            elif self.check_names(token, ['enum']):
                node = self.parse_enum_stmt(t)
                node.parent = mnode
                mnode.add_child(node)

            elif self.check_names(token, ['message']):
                node = self.parse_message_stmt(t)
                node.parent = mnode
                mnode.add_child(node)

            elif token.type == TOKEN_OP and token.value == '}':
                break

        logger.debug('End message node %s [%s:%s]', message_name, t.line, t.column)
        return mnode

    def parse_extensions_stmt(self, t):
        """
            # extension numbers must not overlap with field or other extension numbers;
            extensions = 'extensions' extension ( ',' extension )* ';';

            extension = intLit ( 'to' ( intLit | 'max' ) )?;
        """
        ext = ExtensionsNode()
        ext.start = int(t.next_token().value)

        # check if a to exists
        totoken = t.readahead()
        if totoken.value == 'to':
            totoken = t.next_token()
            next = t.next_token().value
            if next == 'max':
                ext.end = -1
            else:
                ext.end = int(next)

        self.read_semi(t)
        return ext

    def parse_syntax_stmt(self, t):
        node = SyntaxNode()
        self.read_equals(t)
        node.value = self.read_string(t).value
        self.read_semi(t)
        logger.debug('Read syntax node %s', node)
        return node

    def parse_enum_stmt(self, t):
        """
            enum ='enum' ident '{' ( option | enumField | ';' )* '}';

            enumField =ident '=' intLit ';';
        """
        enum = EnumNode()
        enum.name = t.next_token().value
        self.assert_read(t, TOKEN_OP, '{')
        while t.has_next():
            token = t.readahead()

            if token.type == TOKEN_OP and token.value == '}':
                t.skip()
                break
            if token.type == TOKEN_SPACE:
                t.skip(line=1 if token.value == "\n" else 0)
            elif self.check_names(token, ["option"]):
                t.next_token()
                enum.add_child(self.parse_option_stmt(t))
            elif self.check_single_line_comment(token):
                node = self.read_single_line_comment(t)
                enum.add_child(node)
            elif self.check_multiline_line_comment(t, token):
                self.protonode.add_child(self.read_multi_line_comment(t))
            elif token.type == TOKEN_NAME:
                enum.add_child(self.parse_enumassignment_stmt(t))
            else:
                raise Exception("Error parsing enum")
        logger.debug('Read enum %s', enum)
        return enum

    def parse_enumassignment_stmt(self, t):
        enumassign = EnumAssignmentNode()
        enumassign.name = t.next_token().value
        self.read_equals(t)
        enumassign.value = self.read_name(t)
        self.read_semi(t)
        return enumassign

    def parse_extend_stmt(self, t):
        """
            extend ='extend' userType '{' ( field | group | ';' )* '}';
        """
        extend = ExtendNode()
        extend.name = t.read_id()

        # skip the open brace
        token = t.next_token()

        while t.has_next():
            token = t.next_token()
            if token.type == TOKEN_OP and token.value == '}':
                break
            elif self.check_single_line_comment(token):
                node = self.read_single_line_comment(t)
                extend.add_child(node)
            elif self.check_multiline_line_comment(t, token):
                self.protonode.add_child(self.read_multi_line_comment(t))
            elif token.value == 'optional':
                t.backtrack()
                extend.add_child(self.parse_field_desc(t))
            elif token.value in ["\n"]:
                pass
            else:
                self.raise_token_error(token, "Unexpected token: %s" % token)
        return extend

    def parse_import_stmt(self, t):
        """ import ='import' strLit ';';
        """
        # TODO: handle import public strLit;
        
        import_path = self.read_string_or_id(t)
        semi = t.next_token()
        self.assert_token_expression(semi.type == TOKEN_OP and semi.value == ';', semi,  'Expected semicolon')
        node = ImportNode()
        node.value = import_path.value
        logger.debug('Read import node %s', node)
        return node

    def parse_package_stmt(self, t):
        """ package ='package' ident ( '.' ident )* ';';
        """
        package_name = t.read_id()
        semi = self.read_semi(t)
        package = PackageDefinition()
        package.name = package_name

        logger.debug('Read package node %s', package)

        # update name of the the root package node
        self.root.name = package_name

        return package

    def parse_field_desc(self, t):
        """
            field =label type ident '=' intLit ( '[' fieldOption ( ',' fieldOption )* ']' )? ';';
            # tag number must be 2^29-1 or lower, not 0, and not 19000-19999 (reserved);

            fieldOption =optionBody | 'default' '=' constant;
        """
        fdn = FieldDescriptorNode()
        fdn.label = t.next_token().value
        fdn.type = t.read_id()
        fdn.name = t.next_token().value
        equals = t.next_token()
        self.assert_token_expression(equals.type == TOKEN_OP and equals.value == '=', equals, "Missing equals. Got %s" % str(equals))
        number = t.next_token()
        self.assert_token_expression(number.type == TOKEN_NUMBER, number, "Tag should be a number")
        if number.value.startswith('0x'):
            fdn.number = int(number.value, 16)
        else:
            fdn.number = int(number.value, 10)

        # group nodes have a braces after with a list of fielddesc inside
        if fdn.type == "group":
            next = t.readahead()
            self.assert_token_expression(next.value == '{', next, "Expected {")
            fdn.children = self.parse_group_body(t)
            logger.debug('Parse group body %s', fdn.children)
            #next = t.readahead()
            #assert next.value == '}' 
        else:
            next = t.readahead()
            if next.value == '[':
                brace = t.next_token()

                while t.has_next():
                    name, value = self.parse_field_desc_attr(t)
                    if name == 'default':
                        fdn.default = value
                    logger.debug('Parsed field attr %s: %s', name, value)

                    next = t.next_token()

                    if next.value == ']':
                        break
                    elif next.value == ',':
                        logger.debug('read next field')
                        pass

            self.read_semi(t)
        logger.debug('Read field %s', fdn)
        return fdn

    def parse_group_body(self, t):
        children = []
        while t.has_next():
            token = t.next_token()

            if token.type == TOKEN_NAME and token.value in ['optional', 'repeated', 'required']:
                # allow parse_field_desc to read the field label
                t.backtrack()
                node = self.parse_field_desc(t)
                children.append(node)
            elif token.type == TOKEN_OP and token.value == '}':
                #t.backtrack()
                break
        return children

    def parse_field_desc_attr(self, t):
        name = []
        next = t.next_token()
        logger.debug('Field desc start %s', next)
        if next.type == TOKEN_OP and next.value == "(":
            logger.debug('Read option')
            next = t.next_token()
            name.append(next.value)
            self.assert_read(t, TOKEN_RPAR, ')')
        else:
            name.append(next.value)
            logger.debug('Read k/v: %s %s', ''.join(name), next.value)

        #next = t.next_token()
        logger.debug('NEXT IS %s', next)
        self.read_equals(t)


        value = self.read_string_or_dotted(t)

        return ''.join(name).strip("\"'"), value.value
