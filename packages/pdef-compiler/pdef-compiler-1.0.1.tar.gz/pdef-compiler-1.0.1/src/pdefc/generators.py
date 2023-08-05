# encoding: utf-8
import inspect
import io
import logging
import os
import pkg_resources
from jinja2 import Environment

GENERATORS_ENTRY_POINT = 'pdefc.generators'
ENCODING = 'utf8'


class Generator(object):
    '''Abstract code generator, subclass it and implement the generate method.

    @param out          Generated files destination (directory).
    @module_names       List of tuples, [('pdef.module', 'language.module')].
    @prefixes           List of tuples, [('pdef.module', 'ClassPrefix')].
    '''
    def __init__(self, out, module_names=None, prefixes=None, **kwargs):
        self.out = out
        self.module_mapper = ModuleMapper(module_names)
        self.prefix_mapper = PrefixMapper(prefixes)

    def generate(self, package):
        raise NotImplementedError

    def write_file(self, filename, text):
        '''Write a text file to the output directory, filename can contain subdirectories.'''
        # Join the filename with the destination directory.
        filepath = os.path.join(self.out, filename)

        # Create a directory with its children for a file.
        dirpath = os.path.dirname(filepath)
        mkdir_p(dirpath)

        # Write the file contents.
        with io.open(filepath, 'wt', encoding=ENCODING) as f:
            f.write(text)
        logging.info('Created %s', filepath)


def find_generators(entry_point=GENERATORS_ENTRY_POINT):
    '''Dynamically load the source code generators, return a dict {name: generator}.'''
    result = {}
    for entry_point in pkg_resources.iter_entry_points(group=entry_point):
        name = entry_point.name
        generator = entry_point.load()
        result[name] = generator
        logging.debug('Loaded a source code generator %r', name)

    return result


class Templates(object):
    '''Templates class is a default Jinja templates loader relative to a directory or a file.

    Get a template::
        >>> templates = Templates(__file__)
        >>> templates.get('my_jinja.jinja2')

    Render a template::
        >>> templates = Templates(__file__)
        >>> templates.render('mytemplate.jinja2', key='value')

    '''
    def __init__(self, dir_or_file, filters=None):
        '''Create a templates loader relative to a directory or a file.'''
        if os.path.isdir(dir_or_file):
            self._dir = dir_or_file
        else:
            self._dir = os.path.dirname(dir_or_file)

        self._env = Environment(trim_blocks=True, lstrip_blocks=True)
        self._cache = {}

        self.add_filter('upper_first', upper_first)
        if isinstance(filters, dict):
            self.add_filters(**filters)
        elif filters:
            self.add_filters_from_methods(filters)

    def add_filter(self, name, filter0):
        self._env.filters[name] = filter0
        logging.debug('Added a template filter "%s"' % name)

    def add_filters(self, **name_to_filter):
        for name, filter0 in name_to_filter.items():
            self.add_filter(name, filter0)

    def add_filters_from_methods(self, obj):
        for name in dir(obj):
            if name.startswith('_'):
                continue

            attr = getattr(obj, name)
            if inspect.ismethod(attr):
                self.add_filter(name, attr)

    def get(self, name):
        '''Read and return a Jinja template, the templates are cached.'''
        if name in self._cache:
            return self._cache[name]

        # Get the template file.
        path = os.path.join(self._dir, name)
        with open(path, 'r') as module_file:
            text = module_file.read()

        template = self._env.from_string(text)
        self._cache[name] = template

        return template

    def render(self, template_name, **kwargs):
        '''Get a template and render it using the keyword arguments.'''
        template = self.get(template_name)
        return template.render(**kwargs)


class PrefixMapper(object):
    '''Maps pdef names to class prefixes.

    Example::
        >>> mapper = PrefixMapper([('pdef', 'Pd')])
        >>> mapper.get_prefix('pdef.tests')
        >>> 'Pd'
    '''
    def __init__(self, name_prefix_pairs=None):
        self._pairs = tuple((name, prefix) for name, prefix in name_prefix_pairs) \
            if name_prefix_pairs else ()

    def get_prefix(self, name):
        '''Returns a prefix for a name or an empty string, correctly handles relative names.'''
        for module_name, prefix in self._pairs:
            if module_name == name:
                return prefix

            if name.startswith(module_name + '.'):
                return prefix

        return ''


class ModuleMapper(object):
    '''Maps pdef modules to language specific modules.

    Example::
        >>> mapper = ModuleMapper([('pdef.tests', 'tests')])
        >>> mapper.get_module('pdef.tests.messages')
        >>> 'tests.messages'

    '''
    def __init__(self, name_pairs=None):
        self._pairs = tuple((old, new) for old, new in name_pairs) if name_pairs else ()

    def __call__(self, module_name):
        return self.get_module(module_name)

    def get_module(self, name):
        '''Maps a pdef name to a language name, correctly handles relative names.'''
        for old, new in self._pairs:
            if name == old:
                # Full match, service.module => service_module.
                return new

            if name.startswith(old + '.'):
                return new + name[len(old):]

        return name


def upper_first(s):
    '''Uppercase the first letter in a string.'''
    if not s:
        return s
    return s[0].upper() + s[1:]


def mkdir_p(dirname):
    '''Make directories, ignore errors'''
    if os.path.exists(dirname):
        return
    os.makedirs(dirname)
