# encoding: utf-8
import logging
from pdefc.lang.common import Located


class AbstractImport(Located):
    '''AbstractImport is a base class for module imports.'''
    def __init__(self, location=None):
        self.location = location
        self.alias_module_pairs = []

    def link(self, package):
        '''Link this import and return a list of errors.'''
        return []


class AbsoluteImport(AbstractImport):
    '''AbsoluteImport references a single module by its absolute name.'''
    def __init__(self, name, location=None):
        super(AbsoluteImport, self).__init__(location=location)
        self.name = name

    def __str__(self):
        return 'import ' + self.name

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    def link(self, package):
        logging.debug('Linking %s', self)

        module = package.lookup_module(self.name)
        if not module:
            return [self._error('Module not found "%s"', self.name)]

        self.alias_module_pairs = [(self.name, module)]
        return []


class RelativeImport(AbstractImport):
    '''RelativeImport references modules with a prefix and multiple relative names,
    i.e, from my_package import module0, module1.'''
    def __init__(self, prefix, relative_names, location=None):
        super(RelativeImport, self).__init__(location=location)

        self.prefix = prefix
        self.relative_names = tuple(relative_names)

    def __str__(self):
        return '"from ' + self.prefix + ' import ' + ', '.join(self.relative_names) + '"'

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self, hex(id(self)))

    def link(self, package):
        logging.debug('Linking \'%s\'', self)

        errors = []
        for rname in self.relative_names:
            fullname = self.prefix + '.' + rname

            module = package.lookup_module(fullname)
            if module:
                self.alias_module_pairs.append((rname, module))
            else:
                errors.append(self._error('Module not found "%s"', fullname))

        return errors
