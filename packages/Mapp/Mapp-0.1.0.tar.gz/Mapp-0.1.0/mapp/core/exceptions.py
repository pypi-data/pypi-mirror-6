'''
This module contains specific MAPP exceptions.

Created on Dec 3, 2013
'''

class MappError(Exception):
    ''' This exception contains .header of error and error's .description.'''
    def __init__(self, header, description):
        self.header = header
        self.description = description
        Exception.__init__(self, header + "\n" + description)