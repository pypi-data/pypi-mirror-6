# encoding: utf-8
import logging


class Location(object):
    def __init__(self, lineno):
        self.lineno = lineno

    def __str__(self):
        return 'line %s' % self.lineno

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.lineno, hex(id(self)))

    def __eq__(self, other):
        if other is None:
            return False

        if self.__class__ != other.__class__:
            return False

        return self.lineno == other.lineno

    def __hash__(self):
        return self.lineno


class Located(object):
    location = None

    def _error(self, msg, *args):
        '''Shortcut for errors.'''
        location = self.location

        if not location or not location.lineno:
            return msg % args
        s = 'Line %s, %s' % (location.lineno, (msg % args))
        logging.debug(s)
        return s


class Validatable(object):
    is_valid = None
    validated = False
    validation_errors = ()

    def validate(self):
        '''Validate this object and return a list of errors.'''
        if self.validated:
            return self.validation_errors

        errors = self._validate()
        self.is_valid = not errors
        self.validated = True
        self.validation_errors = tuple(errors)

        return self.validation_errors

    def _validate(self):
        '''Override this method in a subclass.'''
        return []
