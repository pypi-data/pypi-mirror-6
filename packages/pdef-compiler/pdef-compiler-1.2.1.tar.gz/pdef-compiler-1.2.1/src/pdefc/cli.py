# encoding: utf-8
import argparse
import logging
import sys
import time

import pdefc


def main(argv=None):
    '''Run the compiler command-line interface.'''
    cli = Cli()
    cli.run(argv)


class Cli(object):
    '''Pdef command-line interface.'''
    def __init__(self, compiler=None):
        # Logging must be configured before any log messages.
        self._setup_logging()

        self.compiler = compiler or pdefc.create_compiler()
        self.commands = self._create_commands(self.compiler)
        self.debug = False

    def run(self, argv=None):
        try:
            parser = self._create_parser()
            args = parser.parse_args(argv)
            logging.debug('Arguments: %s', args)

            # The command_func is set in each command parser.
            func = args.command_func
            if not func:
                raise ValueError('No command_func in %s' % args)

            return func(args)

        except Exception as e:
            if self.debug:
                raise

            # Get rid of the traceback.
            logging.error('%s', e)
            sys.exit(1)

    def _setup_logging(self, argv=None):
        argv = argv or sys.argv

        level = logging.WARN
        if ('-v' in argv) or ('--verbose' in argv):
            level = logging.INFO
        elif '--debug' in argv:
            level = logging.DEBUG
            self.debug = True

        logging.basicConfig(level=level, format='%(message)s')

    def _create_commands(self, compiler):
        commands = [CheckCommand(compiler)]

        for name, cls in self.compiler.generator_classes.items():
            try:
                command = GenerateCommand(self.compiler, name, cls)
                commands.append(command)
            except Exception as e:
                raise pdefc.CompilerException('Failed to create a generator, name=%s, e=%s'
                                              % (name, e.__class__.__name__))
        
        commands.append(VersionCommand(compiler))
        return commands

    def _create_parser(self):
        parser = argparse.ArgumentParser(description=
            'Pdef compiler, see code-generators at http://github.com/pdef')
        parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
        parser.add_argument('--debug', action='store_true', help='debug output')

        subparsers = parser.add_subparsers(dest='command', title='commands',
                                           description='Run "pdefc command -h" for a command help')
        for command in self.commands:
            command.build(subparsers)

        return parser


class Command(object):
    '''Abstract CLI command.'''
    def __init__(self, compiler):
        self.compiler = compiler

    def build(self, subparsers):
        pass

    def execute(self, args):
        pass


class VersionCommand(Command):
    def build(self, subparsers):
        p = subparsers.add_parser('version', help='display the compiler version')
        p.set_defaults(command_func=self.execute)
    
    def execute(self, args):
        print self.compiler.version


class CheckCommand(Command):
    def build(self, subparsers):
        p = subparsers.add_parser('check', help='check a package')
        p.set_defaults(command_func=self.execute)
        p.add_argument('package', help='path to a package yaml file')
        p.add_argument('--path', dest='paths', action='append', default=[],
                       help='add a path to a package dependency')

    def execute(self, args):
        package = args.package
        paths = args.paths

        compiler = self.compiler
        compiler.add_paths(*paths)
        return compiler.check(package)


class GenerateCommand(Command):
    def __init__(self, compiler, generator_name, generator_class):
        super(GenerateCommand, self).__init__(compiler)

        self.generator_name = generator_name
        self.generator_cli = generator_class.create_cli()

        self.command = 'generate-%s' % generator_name
        self.help = generator_class.__doc__

    def build(self, subparsers):
        parser = subparsers.add_parser(self.command, help=self.help)
        parser.add_argument('package', help='path to a package yaml file')
        parser.add_argument('--out', dest='out', required=True,
                            help='directory for the generated files')
        parser.add_argument('--path', dest='paths', action='append', default=[],
                            help='add a path to a package dependency')
        parser.set_defaults(command_func=self.execute)
        self.generator_cli.build_parser(parser)

    def execute(self, args):
        out = args.out
        paths = args.paths
        package_path = args.package

        # Init the compiler.
        compiler = self.compiler
        compiler.add_paths(*paths)

        # Create a generator.
        generator = self.generator_cli.create_generator(out, args)

        # Compile the package.
        package = compiler.compile(package_path)

        t0 = time.time()
        # Generate the source code.
        generator.generate(package)

        # Measure and long the code generation time.
        t = (time.time() - t0) * 1000
        logging.info('Generated %s code in %dms', self.generator_name, t)
