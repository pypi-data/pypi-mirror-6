# encoding: utf-8
import io
import logging
import os
import sys

try:
    # Python2.7
    import urllib2
    from urllib2 import urlopen
    from urlparse import urlparse, urljoin
except ImportError:
    # Python3+
    from urllib.request import urlopen
    from urllib.parse import urlparse, urljoin

from pdefc import CompilerException
from pdefc.lang.packages import PackageInfo


MODULE_EXT = '.pdef'
PACKAGE_EXT = '.yaml'
MODULE_SEP = '/'
UTF8 = 'utf-8'


def create_sources(paths=None):
    return Sources(paths)


class Sources(object):
    '''Package sources.'''
    def __init__(self, paths=None):
        self._sources = {}  # Package names to sources.
        self._files = {}    # Absolute file names to sources.

        if paths:
            for path in paths:
                self.add_path(path)

    def _create_file_source(self, filename):
        return FileSource(filename)

    def _create_url_source(self, url):
        return UrlSource(url)

    def add_source(self, source):
        '''Add a package source, raise CompilerException if a duplicate package.'''
        name = source.name
        if name in self._sources:
            raise CompilerException('Duplicate package source "%s"' % source)

        self._sources[name] = source
        logging.debug('Added a source "%s"' % source)
        return source

    def add_path(self, path):
        '''Add a source path.'''
        if os.path.isdir(path):
            return self._walk_directory(path)
        return self.read_path(path)

    def read_path(self, path):
        '''Read a package source path, add and return the source.'''
        if os.path.isfile(path):
            return self.read_file(path)
        elif _is_url(path):
            return self.read_url(path)

        raise CompilerException('Unsupported path: %s' % path)

    def read_url(self, url):
        '''Read a package source url, add and return the source.'''
        source = self._create_url_source(url)
        self.add_source(source)
        return source

    def read_file(self, filename):
        '''Read a package source file, add and return the source.'''
        absolute = os.path.abspath(filename)
        if absolute in self._files:
            logging.debug('Package file is already present: %s', absolute)
            return self._files[absolute]

        source = self._create_file_source(filename)
        self._files[absolute] = source
        return self.add_source(source)

    def get(self, package_name):
        '''Return a package source by a package name.'''
        source = self._sources.get(package_name)
        if not source:
            raise CompilerException('Package not found "%s"' % package_name)

        return source

    def _walk_directory(self, dirname, package_ext=PACKAGE_EXT):
        if not os.path.exists(dirname):
            raise CompilerException('Directory does not exist: %s' % dirname)

        if not os.path.isdir(dirname):
            raise CompilerException('Not a directory: %s' % dirname)

        result = {}
        for root, dirs, files in os.walk(dirname):
            for file0 in files:
                ext = os.path.splitext(file0)[1]
                if ext.lower() != package_ext:
                    continue

                filename = os.path.join(root, file0)
                self.read_file(filename)

        return result


class Source(object):
    '''Package source.'''
    name = None     # Package name
    info = None     # Package info

    def module(self, module_name):
        '''Return a module source.'''
        raise NotImplementedError

    def module_path(self, module_name):
        '''Return a debug module path which can be used in errors, logs, etc.'''
        raise NotImplementedError

    def _module_filename(self, module_name, ext=MODULE_EXT, sep=MODULE_SEP):
        return module_name.replace('.', sep) + ext


class InMemorySource(Source):
    def __init__(self, info, modules_to_sources=None):
        self.name = info.name
        self.info = info
        self.modules = dict(modules_to_sources) if modules_to_sources else {}

    def module(self, module_name):
        return self.modules.get(module_name)

    def module_path(self, module_name):
        return self._module_filename(module_name)


class FileSource(Source):
    def __init__(self, filename):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        s = self._read(filename)

        try:
            self.info = PackageInfo.from_yaml(s)
            self.name = self.info.name
        except Exception as e:
            raise CompilerException('Failed to read package info: %s, e=%s' % (filename, e))

    def __str__(self):
        return self.filename

    def __repr__(self):
        return '<FileSource %r, file=%r at %s>' % (self.name, self.filename, hex(id(self)))

    def module(self, module_name):
        filepath = self.module_path(module_name)
        return self._read(filepath)

    def module_path(self, module_name):
        filename = self._module_filename(module_name)
        return os.path.join(self.dirname, filename)

    def _read(self, filepath):
        if not os.path.exists(filepath):
            raise CompilerException('File does not exist: %s' % filepath)

        try:
            with io.open(filepath, 'r', encoding=UTF8) as f:
                return f.read()
        except Exception as e:
            raise CompilerException('Failed to read a file: %s, e=%s' % (filepath, e))


class UrlSource(Source):
    def __init__(self, url):
        self.url = url
        self._delegate = None

    def __str__(self):
        if not self._delegate:
            return self.url
        return self.url

    def __repr__(self):
        return '<UrlSource url=%r at %s>' % (self.url, hex(id(self)))

    @property
    def name(self):
        return self.delegate().name

    @property
    def info(self):
        return self.delegate().info

    def module(self, module_name):
        return self.delegate().module(module_name)

    def module_path(self, module_name):
        filename = self._module_filename(module_name)
        return urljoin(self.url, filename)

    def delegate(self):
        if self._delegate:
            return self._delegate

        package_json = self._fetch(self.url)
        info = PackageInfo.from_yaml(package_json)

        modules = {}
        for name in info.modules:
            url = self.module_path(name)
            modules[name] = self._fetch(url)

        self._delegate = InMemorySource(info, modules)
        return self._delegate

    def _fetch(self, url):
        logging.warn('Downloading %s', url)
        try:
            req = self._download(url)
            data = req.read()
            return data.decode(encoding=UTF8)
        except Exception as e:
            raise CompilerException('%s: %s' % (e, url))

    def _download(self, url):
        return urlopen(url)


def _is_url(s):
    if not s:
        return False

    scheme = urlparse(s).scheme
    return scheme and scheme.lower() in ('http', 'https', 'ftp')
