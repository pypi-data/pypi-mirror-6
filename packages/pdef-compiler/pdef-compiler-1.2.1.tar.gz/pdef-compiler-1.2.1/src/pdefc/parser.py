# encoding: utf-8
from __future__ import unicode_literals
import functools
import logging
import re
import ply.lex as lex
import ply.yacc as yacc
from pdefc import CompilerException

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
        #   the parser is created.
        # - module=self.grammar sets the grammar for a lexer and a parser.
        # - start sets the start grammar rule.

        self.lexer = lex.lex(module=self.grammar, optimize=False, debug=False, reflags=re.UNICODE)
        self.parser = yacc.yacc(module=self.grammar, optimize=False, write_tables=False,
                                start='module', debug=False)

        # These are cleaned on each parse invocation.
        self._module_name = None
        self._errors = None

    def parse_sources(self, sources):
        '''Parse module sources and return a list of modules or raise a CompilerException.'''
        errors = []
        modules = []

        for source in sources:
            name = source.name
            data = source.data
            path = source.path

            module, errors0 = self.parse(data, name=name, path=path)
            errors += errors0
            if module:
                modules.append(module)

        # Raise a compiler exception on errors.
        if errors:
            raise CompilerException('Parsing errors', errors)

        return modules

    def parse(self, s, name=None, path=None):
        '''Parse a module from a string, return the module and a list of errors.'''
        logging.info('Parsing %s', path or name or 'stream')

        # Clear the variables.
        self._module_name = name
        self._errors = []

        try:
            lexer = self.lexer.clone()
            module = self.parser.parse(s, tracking=True, lexer=lexer)
            errors = list(self._errors)
            if module:
                module.path = path

            if errors:
                module = None
                self._log_errors(errors, name)
            return module, errors

        finally:
            self._module_name = None
            self._errors = None

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
    ids = types + ('FROM', 'IMPORT', 'NAMESPACE')
    ids_map = {s.lower(): s for s in ids}
    reserved = set(RESERVED)

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

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_]{1}[a-zA-Z0-9_]*'
        t.type = self.ids_map.get(t.value, 'IDENTIFIER')
        
        if t.value in self.reserved:
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
        t.value = cleanup_docstring(t.value)
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
        module : doc namespace imports definitions
        '''
        name = self._name()
        doc = p[1]
        namespace = p[2]
        imports = p[3]
        definitions = p[4]
        p[0] = pdefc.lang.Module(name, namespace=namespace, imports=imports,
                                 definitions=definitions, doc=doc)

    def p_absolute_name(self, p):
        '''
        absolute_name : absolute_name_list
        '''
        p[0] = '.'.join(p[1])

    def p_absolute_name_list(self, p):
        '''
        absolute_name_list : absolute_name_list DOT IDENTIFIER
                           | IDENTIFIER
        '''
        self._list(p, separated=True)

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

    def p_namespace(self, p):
        '''
        namespace : NAMESPACE absolute_name SEMI
        '''
        p[0] = p[2]

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
        import : single_import
               | batch_import
        '''
        p[0] = p[1]

    def p_single_import(self, p):
        '''
        single_import : IMPORT absolute_name SEMI
        '''
        p[0] = pdefc.lang.SingleImport(p[2])

    def p_batch_import(self, p):
        '''
        batch_import : FROM absolute_name IMPORT batch_import_names SEMI
        '''
        p[0] = pdefc.lang.BatchImport(p[2], p[4])

    def p_batch_import_names(self, p):
        '''
        batch_import_names : batch_import_names COMMA absolute_name
                           | absolute_name
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
        self._list(p, separated=True)

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
        interface : interface_exc INTERFACE IDENTIFIER interface_base LBRACE methods RBRACE
        '''
        exc = p[1]
        name = p[3]
        base = p[4]
        methods = p[6]

        p[0] = pdefc.lang.Interface(name, base=base, exc=exc, methods=methods)

    def p_interface_base(self, p):
        '''
        interface_base : COLON type
                       | empty
        '''
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None

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
        def_ref : absolute_name
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


_docstring_start_pattern = re.compile('^\s*/\*\*\s*')   # /**
_docstring_line_pattern = re.compile('^\s*\*\s?')       #  *
_docstring_end_pattern = re.compile('\s*\*/\s*$')       #  */


def cleanup_docstring(s):
    '''Clean up docstrings from start/end and line stars (*).'''
    lines = s.splitlines()
    result = []
    count = 0

    for line in lines:
        count += 1
        first = count == 1
        last = len(lines) == count

        # Strip the docstrings start pattern /**
        if first:
            line = _docstring_start_pattern.sub('', line)

        # String the docstrings end pattern */
        if last:
            line = _docstring_end_pattern.sub('', line)

        # Strip ap optional line start star *.
        if not first:
            line = _docstring_line_pattern.sub('', line)

        # Skip empty first and last lines.
        if not line and (first or last):
            continue
        result.append(line)

    return '\n'.join(result)
