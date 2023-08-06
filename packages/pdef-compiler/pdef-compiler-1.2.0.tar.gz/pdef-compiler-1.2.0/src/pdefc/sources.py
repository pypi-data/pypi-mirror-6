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


PACKAGE_EXT = '.yaml'
UTF8 = 'utf-8'


def create_sources(paths=None):
    return PackageSources(paths)


class PackageSources(object):
    '''Package sources.'''
    def __init__(self, paths=None):
        self._sources = []
        self._paths = {}    # Paths to sources.

        for path in (paths or []):
            self.add_path(path)

    def get(self, package_name):
        '''Return a package source by a package name.'''
        for source in self._sources:
            if source.package_name == package_name:
                return source

        raise CompilerException('Package not found "%s"' % package_name)

    def add_source(self, source):
        '''Add a package source.'''
        self._sources.append(source)
        logging.debug('Added a source "%s"' % source)
        return source

    def add_path(self, path):
        '''Read a source path and return a package source.'''
        if path in self._paths:
            return self._paths[path]

        if _is_url(path):
            source = self._create_url_source(path)
        else:
            if not os.path.exists(path):
                raise CompilerException('File does not exist: %s' % path)
            source = self._create_file_source(path)

        self._paths[path] = source
        return self.add_source(source)

    def _create_url_source(self, url):
        return UrlPackageSource(url)

    def _create_file_source(self, filename):
        return FilePackageSource(filename)


class ModuleSource(object):
    def __init__(self, name, data, path=None):
        self.name = name
        self.data = data
        self.path = path

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<ModuleSource %r at %s' % (self.name, hex(id(self)))


class PackageSource(object):
    '''Abstract package source.'''
    package_info = None
    module_sources = None

    @property
    def package_name(self):
        return self.package_info.name if self.package_info else None

    def module_filename(self, module_name):
        return module_name.replace('.', '/') + '.pdef'


class InMemoryPackageSource(PackageSource):
    '''In memory package source.'''
    def __init__(self, info, module_sources=None):
        self.package_info = info
        self.module_sources = module_sources or []

    def __str__(self):
        return self.package_info.name if self.package_info else 'unnamed-source'


class ForwardingPackageSource(PackageSource):
    def __init__(self):
        self._delegate = None

    @property
    def package_info(self):
        return self.delegate.package_info

    @property
    def module_sources(self):
        return self.delegate.module_sources

    @property
    def delegate(self):
        if self._delegate:
            return self._delegate

        self._delegate = self._read()
        return self._delegate

    def _read(self):
        raise NotImplementedError


class FilePackageSource(ForwardingPackageSource):
    def __init__(self, filename):
        super(FilePackageSource, self).__init__()
        self.filename = filename

    def __str__(self):
        return self.filename

    def __repr__(self):
        return '<FilePackageSource file=%r at %s>' % (self.filename, hex(id(self)))

    def _read(self):
        data = self._read_file(self.filename)
        info = PackageInfo.from_yaml(data)

        modules = []
        dirname = os.path.dirname(self.filename)
        for module_name in info.modules:
            filename = self.module_filename(module_name)
            filepath = os.path.join(dirname, filename)
            data = self._read_file(filepath)

            module = ModuleSource(module_name, data, path=filepath)
            modules.append(module)

        return InMemoryPackageSource(info, modules)

    def _read_file(self, filepath):
        with io.open(filepath, 'r', encoding=UTF8) as f:
            return f.read()


class UrlPackageSource(ForwardingPackageSource):
    def __init__(self, url):
        super(UrlPackageSource, self).__init__()
        self.url = url

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<UrlPackageSource url=%r at %s>' % (self.url, hex(id(self)))

    def _read(self):
        data = self._fetch_url(self.url)
        info = PackageInfo.from_yaml(data)

        modules = []
        for module_name in info.modules:
            url = self._module_url(module_name)
            data = self._fetch_url(url)

            module = ModuleSource(module_name, data, path=url)
            modules.append(module)

        return InMemoryPackageSource(info, modules)

    def _module_url(self, module_name):
        filename = self.module_filename(module_name)
        return urljoin(self.url, filename)

    def _fetch_url(self, url):
        logging.warn('Downloading %s', url)
        req = self._download(url)
        data = req.read()
        return data.decode(encoding=UTF8)

    def _download(self, url):
        return urlopen(url)


def _is_url(s):
    if not s:
        return False

    scheme = urlparse(s).scheme
    return scheme and scheme.lower() in ('http', 'https', 'ftp')
