# encoding: utf-8
import logging
import time

import pdefc
from pdefc.exc import CompilerException
from pdefc.lang.packages import Package


def create_compiler():
    '''Creates a compiler, the compiler is reusable but not thread-safe.'''
    return Compiler()


class Compiler(object):
    '''Compiler parses and compiles packages. It is reusable but not thread-safe.'''
    def __init__(self, sources=None, parser=None):
        self.parser = parser or pdefc.create_parser()
        self.sources = sources or pdefc.create_sources()
        self.packages = {}

        self._generator_classes = None
    
    @property
    def version(self):
        return 'Pdef Compiler %s' % pdefc.__version__

    @property
    def generator_classes(self):
        '''Return {name: GeneratorClass}.'''
        if self._generator_classes is None:
            self._generator_classes = dict(pdefc.find_generator_classes())
        return self._generator_classes

    def add_paths(self, *paths):
        '''Add source paths.'''
        for path in paths:
            self.sources.add_path(path)

    def check(self, path):
        '''Compile a package, return True if correct, else raise a CompilerException.'''
        package = self.compile(path)
        logging.info('%s is valid', package.name)
        return True

    def compile(self, path):
        '''Compile a package from a path.'''
        t0 = time.time()

        source = self.sources.add_path(path)
        package = self._compile_source(source)

        t = (time.time() - t0) * 1000
        logging.info('Fetched and compiled %s in %dms', package.name, t)
        return package

    def _compile_source(self, source, names=None):
        name = source.package_name
        names = names or set(name)  # Prevents circular dependencies

        # Parse the source.
        package = self._parse_source(source)
        self.packages[name] = package

        # Add the default dependency paths.
        for dep in package.info.dependencies:
            if dep.path:
                self.add_paths(dep.path)

        # Compile the dependencies.
        for dep in package.info.dependencies:
            dep_package = self._get_compiled_packaged(dep.name, names=names)
            package.add_dependency(dep_package)

        # Compile the package.
        package.compile()
        return package

    def _get_compiled_packaged(self, name, names=None):
        '''Return a compiled package by its name or raise a CompilerException.'''
        if name in names:
            raise CompilerException('Circular package dependencies in %s' % name)
        names.add(name)

        # Try to get a compiled package.
        if name in self.packages:
            return self.packages[name]

        # Find a package source.
        source = self.sources.get(name)
        return self._compile_source(source, names=names)

    def _parse_source(self, source):
        '''Parse and return a package, but not its dependencies.'''
        logging.info('Parsing %s', source)

        # Parse module sources.
        modules = self.parser.parse_sources(source.module_sources)

        # Create the package.
        return Package(source.package_name, info=source.package_info, modules=modules)
