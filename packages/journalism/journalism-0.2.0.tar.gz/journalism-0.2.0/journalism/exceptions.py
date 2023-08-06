#!/usr/bin/env python

class NullComputationError(Exception):
    """
    Exception raised if an illogical computation is
    attempted on a Column containing nulls.
    """
    pass

class UnsupportedOperationError(Exception):
    """
    Exception raised when an operation is applied
    to an invalid column type.
    """
    def __init__(self, operation, column):
        self.operation = operation
        self.column = column

    def __unicode__(self):
        return '`%s` is not a supported operation for %s' % (self.operation, type(self.column))

    def __str__(self):
        return str(self.__unicode__())

class ColumnValidationError(Exception):
    """
    Exception raised in a column value can not be
    validated.
    """
    def __init__(self, value, column):
        self.value = value
        self.column = column

    def __unicode__(self):
        return '`%s` is not a valid value for %s' % (self.value, type(self.column))

    def __str__(self):
        return str(self.__unicode__())

class ColumnDoesNotExistError(Exception):
    """
    Exception raised when trying to access a column
    that does not exist.
    """
    def __init__(self, k):
        self.k = k
    
    def __unicode__(self):
        return 'Column `%s` does not exist.' % (self.k)

    def __str__(self):
        return str(self.__unicode())

class RowDoesNotExistError(Exception):
    """
    Exception raised when trying to access a row
    that does not exist.
    """
    def __init__(self, i):
        self.i = i
    
    def __unicode__(self):
        return 'Row `%i` does not exist.' % (self.i)

    def __str__(self):
        return str(self.__unicode())
