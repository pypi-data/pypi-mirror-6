# encoding: utf-8
from pdefc.lang.common import Located, Validatable


class TypeEnum(object):
    '''TypeEnum is an enumeration of all pdef type tokens.'''

    # Base value types.
    BOOL = 'bool'
    INT16 = 'int16'
    INT32 = 'int32'
    INT64 = 'int64'
    FLOAT = 'float'
    DOUBLE = 'double'
    STRING = 'string'
    DATETIME = 'datetime'

    # Collection types.
    LIST = 'list'
    MAP = 'map'
    SET = 'set'

    # User defined data types.
    ENUM = 'enum'
    ENUM_VALUE = 'enum_value'
    MESSAGE = 'message'

    # Interface and void.
    INTERFACE = 'interface'
    VOID = 'void'

    PRIMITIVE_TYPES = (BOOL, INT16, INT32, INT64, FLOAT, DOUBLE, STRING, DATETIME)
    DATA_TYPES = PRIMITIVE_TYPES + (LIST, SET, MAP, ENUM, MESSAGE)
    NATIVE_TYPES = PRIMITIVE_TYPES + (VOID, )
    COLLECTION_TYPES = (LIST, SET, MAP)
    DEFINITION_TYPES = (ENUM, MESSAGE, INTERFACE)

    @classmethod
    def is_primitive(cls, type_enum):
        return type_enum in cls.PRIMITIVE_TYPES

    @classmethod
    def is_data_type(cls, type_enum):
        return type_enum in cls.DATA_TYPES

    @classmethod
    def is_collection(cls, type_enum):
        return type_enum in cls.COLLECTION_TYPES


class Type(Located, Validatable):
    '''Type is a common class for all pdef types. These include native types, definitions,
    collections, and enum values.'''
    def __init__(self, type0, location=None):
        self.type = type0
        self.location = location
        self.is_exception = False

    @property
    def is_primitive(self):
        return self.type in TypeEnum.PRIMITIVE_TYPES

    @property
    def is_data_type(self):
        return self.type in TypeEnum.DATA_TYPES

    @property
    def is_native(self):
        return self.type in TypeEnum.NATIVE_TYPES

    @property
    def is_collection(self):
        return TypeEnum.is_collection(self.type)

    @property
    def is_definition(self):
        return self.type in TypeEnum.DEFINITION_TYPES

    @property
    def is_message(self):
        return self.type == TypeEnum.MESSAGE

    @property
    def is_interface(self):
        return self.type == TypeEnum.INTERFACE

    @property
    def is_enum(self):
        return self.type == TypeEnum.ENUM

    @property
    def is_enum_value(self):
        return self.type == TypeEnum.ENUM_VALUE

    def __str__(self):
        return self.type

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.type, hex(id(self)))


class NativeType(object):
    '''Native type singletons.'''
    BOOL = Type(TypeEnum.BOOL)
    INT16 = Type(TypeEnum.INT16)
    INT32 = Type(TypeEnum.INT32)
    INT64 = Type(TypeEnum.INT64)
    FLOAT = Type(TypeEnum.FLOAT)
    DOUBLE = Type(TypeEnum.DOUBLE)
    STRING = Type(TypeEnum.STRING)
    DATETIME = Type(TypeEnum.DATETIME)
    VOID = Type(TypeEnum.VOID)

    _BY_TYPE = {
        TypeEnum.BOOL: BOOL,
        TypeEnum.INT16: INT16,
        TypeEnum.INT32: INT32,
        TypeEnum.INT64: INT64,
        TypeEnum.FLOAT: FLOAT,
        TypeEnum.DOUBLE: DOUBLE,
        TypeEnum.STRING: STRING,
        TypeEnum.DATETIME: DATETIME,
        TypeEnum.VOID: VOID
    }

    @classmethod
    def get(cls, name):
        '''Return a value by its type or none.'''
        return cls._BY_TYPE.get(name)

    @classmethod
    def all(cls):
        '''Return all native types.'''
        return list(cls._BY_TYPE.values())


class Definition(Type):
    '''Definition is a base for user-specified types. These include messages,
    interfaces and enums.'''

    def __init__(self, type0, name, doc=None, location=None):
        super(Definition, self).__init__(type0, location=location)
        self.name = name
        self.doc = doc
        self.module = None

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    def __str__(self):
        return self.name

    @property
    def package(self):
        return self.module.package if self.module else None

    @property
    def namespace(self):
        return self.module.namespace if self.module else None

    @property
    def fullname(self):
        return self.namespace + '.' + self.name if self.namespace else self.name

    @property
    def referenced_types(self):
        '''Return a set of all types referenced in this definition (in fields, methods, etc).'''
        return set()

    @property
    def imported_definitions(self):
        '''Return a set of referenced definitions which are in imported modules.'''
        result = set()

        # Filter imported definitions.
        for type0 in self.referenced_types:
            if type0.is_enum_value:
                type0 = type0.enum

            if not type0.is_definition:
                continue

            if type0.module == self.module:
                continue

            result.add(type0)
        return result

    def lookup(self, name):
        return self.module.lookup(name) if self.module else None

    def link(self, module):
        '''Link this definition references and return a list of errors.'''
        if self.module:
            raise ValueError('Definition is already linked')

        self.module = module
        return []

    def build(self):
        '''Build this definition after linking and return a list of errors.'''
        return []

    def _is_defined_after(self, another):
        '''Return true if this definition is after another one in one module.'''
        if not self.module or not another.module:
            return True

        if self.module is not another.module:
            return True

        for def0 in self.module.definitions:
            if def0 is another:
                return True

            if def0 is self:
                return False

        raise AssertionError('Unreachable code')
