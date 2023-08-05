# encoding: utf-8
from __future__ import unicode_literals
import functools
import logging
import re
import ply.lex as lex
import ply.yacc as yacc

import pdefc.lang
from pdefc.reserved import RESERVED


def create_parser():
    '''Create a new parser, the parser is reusable but not thread-safe.'''
    return Parser()


class Parser(object):
    '''Pdef parser. It is reusable but not thread-safe.'''

    def __init__(self):
        self.grammar = _Grammar(self._name, self._error)

        # Some docs on options:
        # - optimize=False and write_tables=False force to generate tabmodule each time
        #   parser is created. It is required for production.
        # - module=self.grammar sets the grammar for a lexer and a parser.
        # - start='file' sets the start grammar rule.

        self.lexer = lex.lex(module=self.grammar, optimize=False, debug=False, reflags=re.UNICODE)
        self.parser = yacc.yacc(module=self.grammar, optimize=False, write_tables=False,
                                start='module', debug=False)

        # These are cleaned on each parse invocation.
        self._errors = []
        self._module_name = None
        self._path = None

    def parse(self, source, relative_name, path=None):
        '''Parse a module from a source string, return the module and a list of errors.'''
        name = relative_name
        logging.info('Parsing %s', path or name)

        # Clear the variables.
        self._errors = []
        self._module_name = name
        self._path = path

        try:
            lexer = self.lexer.clone()
            module = self.parser.parse(source, tracking=True, lexer=lexer)
            errors = list(self._errors)

            if module:
                module.relative_name = name
                module.path = path

            if errors:
                self._log_errors(errors, path or name)
                return None, errors

            return module, errors

        finally:
            self._errors = None
            self._path = None

    def _name(self):
        return self._module_name

    def _error(self, msg):
        self._errors.append(msg)

    def _log_errors(self, errors, path):
        logging.error(path)
        for error in errors:
            logging.error('  %s' % error)


def _location(t, token_position):
    lineno = t.lineno(token_position)
    return pdefc.lang.Location(lineno)


def _with_location(token_position):
    def decorator(func):
        def set_location(self, t):
            func(self, t)
            t[0].location = _location(t, token_position)

        functools.update_wrapper(set_location, func)
        return set_location

    return decorator


class _Tokens(object):
    '''Lexer tokens.'''

    # Simple reserved words.
    types = (
        'BOOL',
        'INT16',
        'INT32',
        'INT64',
        'FLOAT',
        'DOUBLE',
        'STRING',
        'DATETIME',
        'VOID',

        'LIST',
        'SET',
        'MAP',

        'ENUM',
        'MESSAGE',
        'EXCEPTION',
        'INTERFACE')

    # Identifier types, see t_IDENTIFIER
    ids = types + ('FROM', 'IMPORT')
    ids_map = {s.lower(): s for s in ids}
    reserved = set(s.lower() for s in RESERVED)

    tokens = ids + (
        'DOT',
        'COLON',
        'COMMA',
        'SEMI',
        'LESS',
        'GREATER',
        'LBRACE',
        'RBRACE',
        'LPAREN',
        'RPAREN',
        'IDENTIFIER',
        'DOC',
        'DISCRIMINATOR',
        'POST',
        'QUERY',
        'THROWS')

    # Regexp for simple rules.
    t_DOT = r'.'
    t_COLON = r'\:'
    t_COMMA = r'\,'
    t_SEMI = r'\;'
    t_LESS = r'\<'
    t_GREATER = r'\>'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    # Regexp for options.
    t_DISCRIMINATOR = r'@discriminator'
    t_POST = r'@post'
    t_QUERY = r'@query'
    t_THROWS = r'@throws'

    # Ignored characters
    t_ignore = " \t"

    doc_start_pattern = re.compile('^\s*\**\s*', re.MULTILINE)
    doc_end_pattern = re.compile('\s\*$', re.MULTILINE)

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_]{1}[a-zA-Z0-9_]*'
        t.type = self.ids_map.get(t.value, 'IDENTIFIER')

        if t.value.lower() in self.reserved:
            self._error('Line %s, "%s" is a reserved word' % (t.lineno, t.value))

        return t

    def t_comment(self, t):
        r'//.*\n'
        t.lexer.lineno += 1
        t.lineno += 1

    # Skip a new line and increment the lexer lineno counter.
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    # Pdef docstring.
    def t_DOC(self, t):
        r'\/\*\*((.|\n)*?)\*\/'
        t.lexer.lineno += t.value.count('\n')
        
        value = t.value.strip('/')
        value = self.doc_start_pattern.sub('', value)
        value = self.doc_end_pattern.sub('', value)
        t.value = value
        return t

    def t_error(self, t):
        self._error("Illegal character '%s', line %s" % (t.value[0], t.lexer.lineno))
        t.lexer.skip(1)

    def _error(self, msg):
        raise NotImplementedError()


class _GrammarRules(object):
    '''Parser grammar rules.'''
    def _name(self):
        raise NotImplementedError

    def _error(self, msg):
        raise NotImplementedError

    # Starting point.
    @_with_location(0)
    def p_module(self, p):
        '''
        module : doc imports definitions
        '''
        name = self._name()
        doc = p[1]
        imports = p[2]
        definitions = p[3]
        p[0] = pdefc.lang.Module(name, imports=imports, definitions=definitions, doc=doc)

    # Any absolute name, returns a list.
    def p_absolute_name(self, p):
        '''
        absolute_name : absolute_name DOT IDENTIFIER
                      | IDENTIFIER
        '''
        self._list(p, separated=True)

    def p_type_name(self, p):
        '''
        type_name : absolute_name
        '''
        p[0] = '.'.join(p[1])

    def p_module_name(self, p):
        '''
        module_name : absolute_name
        '''
        p[0] = '.'.join(p[1])

    # Empty token to support optional values.
    def p_empty(self, p):
        '''
        empty :
        '''
        pass

    def p_doc(self, p):
        '''
        doc : DOC
            | empty
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ''

    def p_imports(self, p):
        '''
        imports : imports import
                | import
                | empty
        '''
        self._list(p)

    @_with_location(1)
    def p_import(self, p):
        '''
        import : absolute_import
               | relative_import
        '''
        p[0] = p[1]

    def p_absolute_import(self, p):
        '''
        absolute_import : IMPORT module_name SEMI
        '''
        p[0] = pdefc.lang.AbsoluteImport(p[2])

    def p_relative_import(self, p):
        '''
        relative_import : FROM module_name IMPORT relative_import_names SEMI
        '''
        p[0] = pdefc.lang.RelativeImport(p[2], p[4])

    def p_relative_import_names(self, p):
        '''
        relative_import_names : relative_import_names COMMA module_name
                              | module_name
        '''
        self._list(p, separated=True)

    def p_definitions(self, p):
        '''
        definitions : definitions definition
                    | definition
                    | empty
        '''
        self._list(p)

    def p_definition(self, p):
        '''
        definition : doc enum
                   | doc message
                   | doc interface
        '''
        d = p[2]
        d.doc = p[1]
        p[0] = d

    @_with_location(2)
    def p_enum(self, p):
        '''
        enum : ENUM IDENTIFIER LBRACE enum_values RBRACE
        '''
        p[0] = pdefc.lang.Enum(p[2], values=p[4])

    def p_enum_values(self, p):
        '''
        enum_values : enum_value_list SEMI
                    | enum_value_list
        '''
        p[0] = p[1]

    def p_enum_value_list(self, p):
        '''
        enum_value_list : enum_value_list COMMA enum_value
                        | enum_value
                        | empty
        '''
        self._list(p, separated=1)

    @_with_location(1)
    def p_enum_value(self, p):
        '''
        enum_value : IDENTIFIER
        '''
        p[0] = pdefc.lang.EnumValue(p[1])

    # Message definition
    @_with_location(3)
    def p_message(self, p):
        '''
        message : message_or_exc IDENTIFIER message_base LBRACE fields RBRACE
        '''
        is_exception = p[1].lower() == 'exception'
        name = p[2]
        base, discriminator_value = p[3]
        fields = p[5]

        p[0] = pdefc.lang.Message(name, base=base, discriminator_value=discriminator_value,
                                 declared_fields=fields, is_exception=is_exception)

    def p_message_or_exception(self, p):
        '''
        message_or_exc : MESSAGE
                       | EXCEPTION
        '''
        p[0] = p[1]

    def p_message_base(self, p):
        '''
        message_base : COLON type LPAREN type RPAREN
                     | COLON type
                     | empty
        '''
        base, discriminator = None, None

        if len(p) == 3:
            base = p[2]
        elif len(p) == 6:
            base = p[2]
            discriminator = p[4]

        if base:
            base.location = _location(p, 2)

        p[0] = base, discriminator

    # List of message fields
    def p_fields(self, p):
        '''
        fields : fields field
               | field
               | empty
        '''
        self._list(p)

    # Single message field
    @_with_location(1)
    def p_field(self, p):
        '''
        field : IDENTIFIER type field_discriminator SEMI
        '''
        name = p[1]
        type0 = p[2]
        is_discriminator = p[3]
        p[0] = pdefc.lang.Field(name, type0, is_discriminator=is_discriminator)

    def p_field_discriminator(self, p):
        '''
        field_discriminator : DISCRIMINATOR
                            | empty
        '''
        p[0] = bool(p[1])

    # Interface definition
    @_with_location(3)
    def p_interface(self, p):
        '''
        interface : interface_exc INTERFACE IDENTIFIER LBRACE methods RBRACE
        '''
        exc = p[1]
        name = p[3]
        methods = p[5]

        p[0] = pdefc.lang.Interface(name, exc=exc, methods=methods)

    def p_interface_exc(self, p):
        '''
        interface_exc : THROWS LPAREN type RPAREN
                      | empty
        '''
        if len(p) == 5:
            p[0] = p[3]
        else:
            p[0] = None

    def p_methods(self, p):
        '''
        methods : methods method
                | method
                | empty
        '''
        self._list(p)

    @_with_location(3)
    def p_method(self, p):
        '''
        method : doc method_post IDENTIFIER LPAREN method_args RPAREN type SEMI
        '''
        doc = p[1]
        is_post = p[2]
        name = p[3]
        args = p[5]
        result = p[7]
        p[0] = pdefc.lang.Method(name, result=result, args=args, is_post=is_post, doc=doc)

    def p_method_post(self, p):
        '''
        method_post : POST
                    | empty
        '''
        p[0] = p[1] == '@post'

    def p_method_args(self, p):
        '''
        method_args : method_args COMMA method_arg
                    | method_arg
                    | empty
        '''
        self._list(p, separated=True)

    @_with_location(2)
    def p_method_arg(self, p):
        '''
        method_arg : doc IDENTIFIER type method_arg_attr
        '''
        attr = p[4]
        is_query = attr == '@query'
        is_post = attr == '@post'
        p[0] = pdefc.lang.MethodArg(p[2], p[3], is_query=is_query, is_post=is_post)

    def p_method_arg_attr(self, p):
        '''
        method_arg_attr : POST
                        | QUERY
                        | empty
        '''
        p[0] = p[1]

    @_with_location(1)
    def p_type(self, p):
        '''
        type : value_ref
             | list_ref
             | set_ref
             | map_ref
             | def_ref
        '''
        p[0] = p[1]

    def p_value_ref(self, p):
        '''
        value_ref : BOOL
                  | INT16
                  | INT32
                  | INT64
                  | FLOAT
                  | DOUBLE
                  | STRING
                  | DATETIME
                  | VOID
        '''
        p[0] = pdefc.lang.reference(p[1].lower())

    def p_list_ref(self, p):
        '''
        list_ref : LIST LESS type GREATER
        '''
        p[0] = pdefc.lang.ListReference(p[3])

    def p_set_ref(self, p):
        '''
        set_ref : SET LESS type GREATER
        '''
        p[0] = pdefc.lang.SetReference(p[3])

    def p_map_ref(self, p):
        '''
        map_ref : MAP LESS type COMMA type GREATER
        '''
        p[0] = pdefc.lang.MapReference(p[3], p[5])

    def p_def_ref(self, p):
        '''
        def_ref : type_name
        '''
        p[0] = pdefc.lang.reference(p[1])

    def p_error(self, p):
        if p is None:
            msg = 'Unexpected end of file'
        else:
            msg = 'Line %s, syntax error at "%s"' % (p.lexer.lineno, p.value)

        self._error(msg)

    def _list(self, p, separated=False):
        '''List builder, supports separated and empty lists.

        Supported grammar:
        list : list [optional separator] item
             | item
             | empty
        '''
        if len(p) == 1:
            p[0] = []
        elif len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = p[1]
            if not separated:
                p[0].append(p[2])
            else:
                p[0].append(p[3])


class _Grammar(_GrammarRules, _Tokens):
    '''Grammar combines grammar rules and lexer tokens. It can be passed to the ply.yacc
    and pla.lex functions as the module argument.'''

    def __init__(self, name_func, error_func):
        self._name = name_func
        self._error = error_func
