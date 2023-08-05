# encoding: utf-8
import argparse
import logging
import sys

import pdefc
from pdefc.exc import CompilerException


def main(argv=None):
    '''Run the compiler command-line interface.'''
    cli = Cli()
    cli.run(argv)


class Cli(object):
    '''Pdef command-line interface.'''
    def _create_compiler(self, paths=None, allow_duplicate_definitions=False):
        return pdefc.create_compiler(paths, allow_duplicate_definitions=allow_duplicate_definitions)

    def _find_generators(self):
        return pdefc.find_generators()

    def run(self, argv=None):
        # Configure logging before the commands, because the latter
        # requires a functional logger.
        self._logging(argv)

        try:
            args = self._parse(argv)

            # The command_func is set in each subparser.
            func = args.command_func
            if not func:
                raise ValueError('No command_func in %s' % args)

            return func(args)

        except pdefc.CompilerException as e:
            # It's an expected exception.
            # Get rid of the traceback.
            logging.error('%s', e)
            sys.exit(1)

    def _parse(self, argv):
        parser = self._create_parser()
        args = parser.parse_args(argv)

        logging.debug('Arguments: %s', args)
        return args

    def _create_parser(self):
        parser = argparse.ArgumentParser(description='Pdef compiler, see http://github.com/pdef')
        subparsers = parser.add_subparsers(dest='command', title='commands',
            description='To show a command help execute "pdefc {command} -h"')

        self._logging_args(parser)
        self._check_args(subparsers)
        self._generate_args(subparsers)
        return parser

    # Logging.

    def _logging(self, argv=None):
        argv = argv or sys.argv

        level = logging.WARN
        if ('-v' in argv) or ('--verbose' in argv):
            level = logging.INFO
        elif '--debug' in argv:
            level = logging.DEBUG

        logging.basicConfig(level=level, format='%(message)s')

    def _logging_args(self, parser):
        parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
        parser.add_argument('--debug', action='store_true', help='debug output')

    # Check.

    def _check(self, args):
        package = args.package
        paths = args.paths
        allow_duplicate_definitions = args.allow_duplicate_definitions

        compiler = self._create_compiler(paths, allow_duplicate_definitions)
        return compiler.check(package)

    def _check_args(self, subparsers):
        parser = subparsers.add_parser('check', help='check a package')
        parser.add_argument('package', help='path to a package yaml file')
        parser.add_argument('--include', dest='paths', action='append', default=[],
                            help='add a path to a package dependency')
        parser.add_argument('--allow-duplicate-definitions', dest='allow_duplicate_definitions',
                            action='store_true', default=False,
                            help='allow duplicate definition names in a package')
        parser.set_defaults(command_func=self._check)

    # Generate.

    def _generate(self, args):
        package = args.package
        generator = args.generator
        paths = args.paths
        out = args.out
        module_names = self._parse_pairs(args.module_names)
        prefixes = self._parse_pairs(args.prefixes)
        allow_duplicate_definitions = args.allow_duplicate_definitions

        compiler = self._create_compiler(paths, allow_duplicate_definitions)
        return compiler.generate(package, generator, out=out, module_names=module_names,
                                 prefixes=prefixes)

    def _generate_args(self, subparsers):
        generators = self._find_generators()
        generator_names = list(generators.keys())
        description = self._generators_description()

        parser = subparsers.add_parser('generate', description=description,
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       help='generate source code from a package')
        parser.add_argument('package', help='path to a package yaml file')
        parser.add_argument('--generator', choices=generator_names, required=True)
        parser.add_argument('--out', dest='out', required=True,
                            help='directory for generated files')
        parser.add_argument('--module', dest='module_names', action='append', default=[],
                            help='map a pdef module to a language module, '
                                 'i.e. "pdef.module:io.pdef.java" (generator specific)')
        parser.add_argument('--prefix', dest='prefixes', action='append', default=[],
                            help='add a prefix to all definitions in a module, '
                                 'i.e. "company.project:Pr (generator specific)')
        parser.add_argument('--include', dest='paths', action='append', default=[],
                            help='add a path to a package dependency')
        parser.add_argument('--allow-duplicate-definitions', dest='allow_duplicate_definitions',
                            action='store_true', default=False,
                            help='allow duplicate definition names in a package')

        parser.set_defaults(command_func=self._generate)

    def _generators_description(self):
        '''Return a generators description string.'''
        generators = dict(self._find_generators())

        description  = ['available generators:']

        for name, generator in generators.items():
            doc = generator.__doc__ or ''

            first = True
            for line in doc.splitlines():
                if first:
                    line = line.strip() or 'no description'
                    description.append('  - %s: %s' % (name, line))
                    first = False
                elif line.strip():
                    description.append(line)

            if first:
                description.append('  - %s: no description' % name)

        description.append('\nmore generators: \n  see https://github.com/pdef/pdef')
        return '\n'.join(description)

    def _parse_pairs(self, seq):
        if not seq:
            return []

        result = []
        error = False
        for item in seq:
            parts = item.split(':')
            if len(parts) != 2:
                logging.error('Wrong pair "%s", the pair must be specified as '
                              '"string.one:string.two"', item)
                error = True
                continue

            old_name, new_name = parts
            result.append((old_name, new_name))

        if error:
            raise CompilerException('Wrong arguments')

        logging.debug('Name mappings %s', result)
        return result
