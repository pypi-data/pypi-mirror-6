#!/usr/localcpython-3.3/bin/python

'''A FIFO (queue), implemented over Linked_list'''

import linked_list_mod

class Fifo(object):
    # pylint: disable=incomplete-protocol

    '''A FIFO (queue), implemented over Linked_list'''

    def __init__(self):
        self.linked_list = linked_list_mod.Linked_list()

    def push(self, data):
        '''Add something to the fifo'''
        self.linked_list.append(data)

    def pop(self):
        '''Remove something from the fifo'''
        if self.linked_list:
            return self.linked_list.popleft()
        else:
            raise IndexError("FIFO empty")

    def peek(self):
        '''Peek at the beginning of the fifo without removing the value'''
        if self.linked_list:
            return self.linked_list.first.data
        else:
            raise IndexError('FIFO empty')

    def __len__(self):
        return len(self.linked_list)

    def __bool__(self):
        '''Return True iff we are nonempty'''
        if self.linked_list:
            return True
        else:
            return False

    __nonzero__ = __bool__
