#!/usr/localcpython-3.3/bin/python

'''A LIFO (stack), implemented over Linked_list'''

import linked_list_mod

class Lifo(object):
    '''A LIFO (stack), implemented over Linked_list'''

    def __init__(self):
        self.linked_list = linked_list_mod.Linked_list()

    def push(self, data):
        '''Add something to the lifo'''
        self.linked_list.prepend(data)

    def pop(self):
        '''Remove something from the lifo'''
        if self.linked_list:
            return self.linked_list.popleft()
        else:
            raise IndexError("LIFO empty")

    def peek(self):
        '''Peek at the beginning of the lifo without removing the value'''
        if self.linked_list:
            return self.linked_list.first.data
        else:
            raise IndexError('LIFO empty')

