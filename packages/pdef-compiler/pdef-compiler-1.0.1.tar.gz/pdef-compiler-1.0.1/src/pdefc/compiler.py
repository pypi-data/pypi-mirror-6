# encoding: utf-8
import logging
import time

import pdefc
from pdefc.exc import CompilerException
from pdefc.lang.packages import Package


def create_compiler(paths=None, allow_duplicate_definitions=False):
    '''Creates a compiler, the compiler is reusable but not thread-safe.'''
    sources = pdefc.create_sources(paths)
    return Compiler(sources, allow_duplicate_definitions=allow_duplicate_definitions)


class Compiler(object):
    '''Compiler parses and compiles packages. It is reusable but not thread-safe.'''
    def __init__(self, sources=None, parser=None, allow_duplicate_definitions=False):
        self.sources = sources or pdefc.create_sources()
        self.parser = parser or pdefc.create_parser()
        self.allow_duplicate_definitions = allow_duplicate_definitions
        self._generators = None

    @property
    def generators(self):
        if self._generators is None:
            self._generators = dict(pdefc.find_generators())
        return self._generators

    def check(self, package_path):
        '''Compile a package from a path, and print a message if its correct.'''
        package = self.compile(package_path)
        logging.info('%s is valid', package.name)

    def compile(self, package_path):
        '''Compile a package from a path.'''
        t0 = time.time()
        source = self.sources.read_path(package_path)
        package = self._compile(source.name, compiled_map=set())

        t1 = time.time()
        t = (t1 - t0) * 1000
        logging.info('Fetched and compiled %s in %dms', package.name, t)
        return package

    def generate(self, package_path, generator_name, out, module_names=None, prefixes=None):
        '''Generate a package from a path.

        @package_path       Path or url to a package yaml file.
        @generator_name     Generator name.
        @module_names       List of tuples, [('pdef.module', 'language.module')].
        @prefixes           List of tuples, [('pdef.module', 'ClassPrefix')].
        '''

        factory = self.generators.get(generator_name)
        if not factory:
            raise CompilerException('Source code generator not found: %s' % generator_name)

        package = self.compile(package_path)
        
        t0 = time.time()
        generator = factory(out, module_names=module_names, prefixes=prefixes)
        generator.generate(package)

        t1 = time.time()
        t = (t1 - t0) * 1000
        logging.info('Generated %s code in %dms', generator_name, t)

    def _compile(self, package_name, compiled_map):
        '''Compile and return a package with its dependencies, prevent circular dependencies.'''

        # Prevent circular package dependencies
        if package_name in compiled_map:
            raise CompilerException('Circular dependency: package=%s' % package_name)
        compiled_map.add(package_name)

        # Parse the package before compiling its dependencies
        # to improve responsiveness.
        package = self._parse(package_name)

        # Compile the package dependencies.
        deps = []
        for depname in package.info.dependencies:
            dependency = self._compile(depname, compiled_map)
            deps.append(dependency)

        # Compile and return the package.
        logging.info('Compiling %s', package_name)
        for dep in deps:
            package.add_dependency(dep)

        errors = package.compile(allow_duplicate_definitions=self.allow_duplicate_definitions)
        if errors:
            raise CompilerException('Compilation errors', errors)

        return package

    def _parse(self, pname):
        '''Parse and return a package, but not its dependencies.'''
        # Find the package source.
        source = self.sources.get(pname)
        info = source.info

        # Init the package.
        logging.info('Parsing %s', source)
        package = Package(pname, info=info)
        assert info.name == pname, 'Package name does not match one in info'

        # Parse package modules.
        errors = []
        modules = []
        for mname in info.modules:
            s = source.module(mname)
            path = source.module_path(mname)

            module, errors0 = self.parser.parse(s, relative_name=mname, path=path)
            errors += errors0
            if module:
                modules.append(module)

        if errors:
            raise CompilerException('Parsing errors', errors)

        for module in modules:
            package.add_module(module)
        return package
