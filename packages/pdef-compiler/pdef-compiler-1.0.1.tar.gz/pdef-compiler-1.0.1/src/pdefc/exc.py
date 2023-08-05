# encoding: utf-8


class CompilerException(Exception):
    def __init__(self, message, errors=None):
        super(CompilerException, self).__init__(message)
        self.errors = errors or ()
