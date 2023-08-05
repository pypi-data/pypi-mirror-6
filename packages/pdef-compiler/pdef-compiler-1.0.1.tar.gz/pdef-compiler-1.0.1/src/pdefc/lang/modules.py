# encoding: utf-8
import logging
from collections import deque
import re

from pdefc.lang.common import Validatable
from pdefc.lang.types import NativeType, TypeEnum


class Module(Validatable):
    '''Module is a named scope for definitions. It is usually a *.pdef file.'''
    name_pattern = re.compile(r'^[a-zA-Z]{1}[a-zA-Z0-9_]*(\.[a-zA-Z]{1}[a-zA-Z0-9_]*)*$')

    def __init__(self, relative_name, imports=None, definitions=None, doc=None, path=None):
        self.relative_name = relative_name
        self.doc = doc
        self.path = path
        self.package = None

        self.imports = []               # imports
        self.imported_aliases = []      # (alias, module) pairs
        self.imported_modules = []      # modules

        self.definitions = []
        self._definition_map = {}       # Performance optimization

        if imports:
            for import0 in imports:
                self.add_import(import0)

        if definitions:
            for def0 in definitions:
                self.add_definition(def0)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    @property
    def name(self):
        if not self.package:
            return self.relative_name

        if self.package.name == self.relative_name:
            return self.relative_name

        return '%s.%s' % (self.package.name, self.relative_name)

    @property
    def imported_definitions(self):
        '''Return a set of imported definitions.'''
        result = set()
        for def0 in self.definitions:
            result.update(def0.imported_definitions)
        
        return result

    def _log_return_errors(self, errors):
        if not errors:
            return []

        logging.error(self.path or self.name)
        for error in errors:
            logging.error('  %s' % error)

        return errors

    def add_import(self, import0):
        '''Add a module import to this module.'''
        self.imports.append(import0)
        logging.debug('%s: added an import "%s"', self, import0)

    def add_imported_module(self, alias, module):
        '''Add an imported module to this module.'''
        self.imported_aliases.append((alias, module))
        self.imported_modules.append(module)

        logging.debug('%s: added an imported module, alias="%s", module="%s"', self, alias, module)

    def get_imported_module(self, alias):
        '''Find a module by its import alias.'''
        for alias1, module in self.imported_aliases:
            if alias1 == alias:
                return module

        return None

    def add_definition(self, def0):
        '''Add a new definition to this module.'''
        self.definitions.append(def0)
        self._definition_map[def0.name] = def0
        logging.debug('%s: added a definition "%s"', self, def0.name)

    def get_definition(self, name):
        '''Return a definition or an enum value in this module by a name.'''

        # Try to get a definition by name.
        if name in self._definition_map:
            return self._definition_map[name]

        # Return if not a relative name.
        if '.' not in name:
            return

        # Try to get an enum value.
        enum_name, value_name = name.split('.', 1)
        if enum_name not in self._definition_map:
            return

        enum = self._definition_map[enum_name]
        if not enum.is_enum:
            return

        return enum.get_value(value_name)

    def lookup(self, name):
        '''Find a definition or enum value in this module or imported modules.'''

        # Try to get a native type.
        def0 = NativeType.get(name)
        if def0:
            return def0

        # Try to find a type or an enum value in the current module.
        def0 = self.get_definition(name)
        if def0:
            return def0

        # Try to find an imported type.
        left = []
        right = name.split('.')
        while right:
            left.append(right.pop(0))
            lname = '.'.join(left)
            rname = '.'.join(right)

            module = self.get_imported_module(lname)
            if not module:
                continue

            # Try to get a definition or an enum value from the imported module.
            def0 = module.get_definition(rname)
            if def0:
                return def0

        return None

    def _depends_on(self, another):
        return bool(self._get_import_path(another))

    def _get_import_path(self, another):
        '''Returns a list of modules when this module depends on another module.

        For example: a imports b, b imports c;
        a._get_import_path_with(c) => [a, b, c]
        '''
        if another is None or another is self:
            return []

        # BFS
        q = deque(self.imported_modules)
        seen = set()
        came_from = {module: self for module in self.imported_modules}

        depends = False
        while q:
            current = q.pop()
            if current in seen:
                continue

            if current is another:
                # Self depends on another!
                depends = True
                break

            seen.add(current)
            q += current.imported_modules
            came_from.update({imported: current for imported in current.imported_modules})

        if not depends:
            return []

        # Reconstruct the path.
        path = [another]
        module = another
        while True:
            module = came_from[module]
            path.append(module)
            if module is self:
                break

        path.reverse()
        return path

    # Link.

    def link(self, package=None):
        '''Link imports and definitions and return a list of errors.'''
        logging.debug('Linking %s as %s', self.path, self)

        if self.package:
            raise ValueError('Module is already linked, module=%s' % self)
        self.package = package

        errors = self._link_imports(package)
        if errors:
            return self._log_return_errors(errors)

        errors = self._link_definitions()
        return self._log_return_errors(errors)

    def _link_imports(self, package):
        '''Link imports, must be called before link_module_defs().'''
        errors = []

        for import0 in self.imports:
            errors += import0.link(package)

            for alias, module in import0.alias_module_pairs:
                self.add_imported_module(alias, module)

        return errors

    def _link_definitions(self):
        '''Link imports and definitions.'''
        errors = []
        for def0 in self.definitions:
            errors += def0.link(self)

        return errors

    # Build.

    def build(self):
        '''Build definitions and return a list of errors.'''
        logging.debug('Building %s', self)

        errors = []
        for def0 in self.definitions:
            errors += def0.build()

        return self._log_return_errors(errors)

    # Validate.

    def _validate(self):
        '''Validate imports and definitions and return a list of errors.'''
        logging.debug('Validating %s', self)
        errors = []
        errors += self._validate_name()
        errors += self._validate_no_duplicate_symbols()

        for def0 in self.definitions:
            errors += def0.validate()

        return self._log_return_errors(errors)

    def _validate_name(self):
        if self.name_pattern.match(self.relative_name):
            return []
        return ['Wrong module name "%s". A name must be one or several words separated by dots, '
                'a word must contain only latin letters, digits and underscores, '
                'and must start with a letter, for example, "users.accounts.events"' % self.name]

    def _validate_no_duplicate_symbols(self):
        errors = []

        # Prevent imports with duplicate aliases.
        names = set()
        for alias, _ in self.imported_aliases:
            if alias in names:
                errors.append('Duplicate import "%s"' % alias)
            names.add(alias)

        # Prevent definitions and imports with duplicate names.
        for def0 in self.definitions:
            name = def0.name
            if name in names:
                errors.append('Duplicate definition or import "%s"' % name)
            names.add(name)

        return errors
