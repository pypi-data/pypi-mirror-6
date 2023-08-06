# encoding: utf-8
import logging

from pdefc.lang import references
from pdefc.lang.common import Located, Validatable
from pdefc.lang.types import TypeEnum, NativeType, Definition


class Interface(Definition):
    '''User-defined interface.'''
    def __init__(self, name, base=None, exc=None, methods=None, doc=None, location=None):
        super(Interface, self).__init__(TypeEnum.INTERFACE, name, doc=doc, location=location)

        self.base = base
        self.exc = exc
        self.declared_methods = []

        if methods:
            for method in methods:
                self.add_method(method)

    @property
    def base(self):
        return self._base.dereference()

    @base.setter
    def base(self, value):
        self._base = references.reference(value)

    @property
    def exc(self):
        return self._exc.dereference()

    @exc.setter
    def exc(self, value):
        self._exc = references.reference(value)

    @property
    def methods(self):
        return self.inherited_methods + self.declared_methods

    @property
    def inherited_methods(self):
        if not self.base:
            return []

        return self.base.methods

    @property
    def referenced_types(self):
        result = set()
        result.update(self._base.referenced_types)
        result.update(self._exc.referenced_types)
        
        for method in self.declared_methods:
            result.update(method._result.referenced_types)
            for arg in method.args:
                result.update(arg._type.referenced_types)
        
        result.discard(self)
        return result

    def add_method(self, method):
        '''Add a method to this interface.'''
        self.declared_methods.append(method)
        logging.debug('%s: added a method "%s"', self, method.name)

    def create_method(self, name, result=NativeType.VOID, arg_tuples=None, is_post=False):
        '''Add a new method to this interface and return the method.'''
        method = Method(name, result=result, is_post=is_post)
        if arg_tuples:
            for arg_tuple in arg_tuples:
                method.create_arg(*arg_tuple)

        self.add_method(method)
        return method

    def link(self, module):
        '''Link the base, the exception and the methods.'''
        errors = super(Interface, self).link(module)
        errors += self._base.link(module.lookup)
        errors += self._exc.link(module.lookup)

        for method in self.declared_methods:
            errors += method.link(self)

        return errors

    def _validate(self):
        logging.debug('Validating %s', self)
        errors = self._validate_base()
        if errors:
            # Cannot validate this interface when an invalid base.
            return errors

        errors += self._validate_methods()
        errors += self._validate_exc()
        return errors

    def _validate_base(self):
        if not self.base:
            return []

        # Prevent circular inheritance before any validation.
        if self._has_circular_inheritance:
            return [self._error('%s: circular inheritance', self)]

        # Validate the base, ignore the errors, they are collected
        # when the base is validated in a module.
        base = self.base
        base.validate()
        if not base.is_valid:
            return [self._error('%s: invalid base %s', self, base)]

        if not base.is_interface:
            return [self._error('%s: base must be an interface not %s', self, base)]

        errors = []
        if not self._is_defined_after(base):
            errors.append(self._error('%s: must be declared after its base %s', self, base))

        # base.module can be None in tests.
        if base.module and base.module._depends_on(self.module):
            path = base.module._get_import_path(self.module)
            errors.append(self._error('%s: cannot inherit %s, '
                                      'it is in a dependent module "%s", import path: %s',
                                      self, base, base.module, path))

        return errors

    @property
    def _has_circular_inheritance(self):
        base = self.base
        while base:
            if base is self:
                return True

            if base.is_interface:
                base = base.base
            else:
                # Cannot proceed, the base is not an interface.
                break

        return False

    def _validate_exc(self):
        if not self.exc:
            return []

        if not self.exc.is_exception:
            return [self._error('%s: exc must be an exception, got %s', self, self.exc)]

        errors = self._exc.validate()
        if errors:
            return errors

        if not self.base or not self.base.exc:
            return []

        # The current exception must match the base exception.
        if self.exc == self.base.exc:
            return []

        return [self._error('%s: subinterface exception must be empty, '
                            'or match the base exception, %s', self, self.exc)]

    def _validate_methods(self):
        errors = []

        # Prevent duplicate methods.
        names = set([method.name for method in self.inherited_methods])
        for method in self.declared_methods:
            if method.name in names:
                errors.append(self._error('%s: duplicate method "%s"', self, method.name))
            names.add(method.name)

        # Validate methods.
        for method in self.declared_methods:
            errors += method.validate()

        return errors


class Method(Located, Validatable):
    '''Interface method.'''
    def __init__(self, name, result=NativeType.VOID, args=None, is_post=False, doc=None,
                 location=None):
        self.name = name
        self.args = []
        self.result = result
        self.interface = None
        self.is_post = is_post

        self.doc = doc
        self.location = location

        if args:
            for arg in args:
                self.add_arg(arg)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    @property
    def result(self):
        return self._result.dereference()

    @result.setter
    def result(self, value):
        self._result = references.reference(value)

    @property
    def is_terminal(self):
        return self.result and self.result.type != TypeEnum.INTERFACE

    def lookup(self, name):
        return self.interface.lookup(name) if self.interface else None

    def add_arg(self, arg):
        '''Append an argument to this method.'''
        if arg.method:
            raise ValueError('Argument is already in a method, %s' % arg)

        self.args.append(arg)
        logging.debug('%s: added an arg "%s"', self, arg.name)

    def create_arg(self, name, definition, is_query=False, is_post=False):
        '''Create a new arg and add it to this method.'''
        arg = MethodArg(name, definition, is_query=is_query, is_post=is_post)
        self.add_arg(arg)
        return arg

    def link(self, interface):
        logging.debug('Linking %s', self)

        if self.interface:
            raise ValueError('Method is already linked, method=%s', self)
        self.interface = interface

        errors = []
        errors += self._result.link(self.lookup)
        for arg in self.args:
            errors += arg.link(self)

        return errors

    def _validate(self):
        logging.debug('Validating %s', self)
        errors = []

        # The method must have a result.
        if not self.result:
            errors.append(self._error('%s: method result required', self))
        else:
            errors += self._result.validate()

        # @post methods must be terminal.
        if self.is_post and not self.is_terminal:
            errors.append(self._error('%s: @post method must be terminal (return a data type '
                                      'or void)', self))

        # Prevent duplicate arguments.
        names = set()
        for arg in self.args:
            if arg.name in names:
                errors.append(self._error('%s: duplicate argument "%s"', self, arg.name))
            names.add(arg.name)

        # Validate post/query arguments.
        is_post = self.is_post
        is_nonpost_terminal = not is_post and self.is_terminal
        for arg in self.args:
            if arg.is_post and not is_post:
                errors.append(self._error(
                    '%s: @post arguments can be declared only in @post methods', self))
                break

            elif arg.is_query and not is_nonpost_terminal:
                errors.append(
                    self._error('%s: @query arguments can be declared only in terminal non-post '
                                'methods', self))
                break

        # Validate arguments.
        for arg in self.args:
            errors += arg.validate()

        return errors


class MethodArg(Located, Validatable):
    '''Single method argument.'''
    def __init__(self, name, type0, is_query=False, is_post=False):
        '''Create a method arg.
        
        @deprecated is_query
        @deprecated is_post
        '''
        self.name = name
        self.type = type0
        self.method = None

        self.is_query = is_query
        self.is_post = is_post

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    @property
    def type(self):
        return self._type.dereference()

    @type.setter
    def type(self, value):
        self._type = references.reference(value)

    @property
    def fullname(self):
        return '%s.%s' % (self.method, self.name)

    def link(self, method):
        if self.method:
            raise ValueError('Method argument is already linked, %s' % self)
        self.method = method

        return self._type.link(method.lookup)

    def _validate(self):
        if not self.type:
            return [self._error('%s: argument type required', self)]
        
        if not self.type.is_data_type:
            return [self._error('%s: argument must be a data type', self)]

        errors = []
        if self.is_post and self.is_query:
            errors = [self._error('%s: argument cannot be both @query and @post', self)]
        
        if self.is_post or self.is_query:
            logging.error('@post and @query argument annotations are deprecated')
        
        errors += self._type.validate()
        return errors
