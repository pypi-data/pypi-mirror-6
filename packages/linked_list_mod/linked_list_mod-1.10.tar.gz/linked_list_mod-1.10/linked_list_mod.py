
'''Singly linked list class.'''

class Linked_list(object):
    # pylint: disable=incomplete-protocol

    '''A class to hold a linked list.  The nodes are a separate structure'''
    def __init__(self, iterator=None):
        self.first = None
        self.last = None
        self.length = 0
        if iterator is not None:
            self.extend(iterator)

    def append(self, data):
        '''Add an element to the end of the list'''
        if self.first is None:
            if self.last is None:
                # The list was completely empty - point first and last at our new node
                new_node = Linked_list_node(data, None)
                self.first = new_node
                self.last = new_node
                self.length = 1
            else:
                # The list has a first element but no last element
                raise AssertionError('List has last but not first?')
        else:
            if self.last is None:
                # The list has a last element but no first element
                raise AssertionError('List has first but not last?')
            else:
                # The list has at least one element already
                new_node = Linked_list_node(data, None)
                self.last.tail = new_node
                self.last = self.last.tail
                self.length += 1

    def prepend(self, data):
        '''Add an element to the beginning of the list'''
        if self.first is None:
            if self.last is None:
                # The list was completely empty - point first and last at our new node
                new_node = Linked_list_node(data, None)
                self.first = new_node
                self.last = new_node
                self.length = 1
            else:
                # The list has a first element but no last element
                raise AssertionError('List has last but not first?')
        else:
            if self.last is None:
                # The list has a last element but no first element
                raise AssertionError('List has first but not last?')
            else:
                # The list has at least one element already
                new_node = Linked_list_node(data, None)
                new_node.tail = self.first
                self.first = new_node
                self.length += 1

    def __nonzero__(self):
        if self.first is None:
            if self.last is None:
                return False
            else:
                raise AssertionError('List has a last but no first')
        else:
            if self.last is None:
                raise AssertionError('List has a first but no last')
            else:
                return True

    __bool__ = __nonzero__

    def __iter__(self):
        '''Iterate over the values of the list'''
        if self:
            current = self.first
            while current:
                yield current.data
                current = current.tail

    def nodes(self):
        '''Iterate over the nodes of the list, not just the values'''
        if self:
            current = self.first
            while current:
                yield current
                current = current.tail

    def __len__(self):
        return self.length

    def reverse(self):
        '''Reverse the elements of the list'''

        # If the list is empty, then there's nothing to do
        if not self:
            return

        # If the list has one element, then there's nothing to do
        if self.first == self.last:
            return

        temp_first = self.first

        previous = None
        current = self.first
        while current:
            tail = current.tail
            current.tail = previous
            previous = current
            current = tail
        self.first = previous

        self.last = temp_first

    def __str__(self):
        return 'Linked_list([ {} ])'.format(', '.join(str(element) for element in self))

    __repr__ = __str__

    def popleft(self):
        '''Remove and return the first element of the list'''
        if self.first is None:
            assert self.last is None
            raise IndexError('Attempt to popleft empty list')
        if self.first is self.last:
            value = self.first.data
            self.first = None
            self.last = None
            self.length -= 1
            return value

        data = self.first.data
        self.first = self.first.tail
        self.length -= 1
        return data

    def remove(self, data):
        # pylint: disable=too-many-branches
        '''Remove an element by value'''

        if self.first is None:
            assert self.last is None
            raise ValueError('Attempt to remove value from empty list')

        if self.first.data == data:
            # first value is what we want to remove
            if self.first is self.last:
                # single-element list, deal with last too
                self.first = None
                self.last = None
                self.length -= 1
                return
            self.first = self.first.tail
            self.length -= 1
            return

        current = self.first
        previous = None
        while current:
            if current.data == data:
                if current is self.last:
                    # this is the last element of the list
                    previous.tail = None
                    self.last = current
                    self.length -= 1
                    return
                previous.tail = previous.tail.tail
                self.length -= 1
                return
            previous = current
            current = current.tail
        raise ValueError('Element not in list')

    def __contains__(self, data):
        for value in self:
            if value == data:
                return True
        return False

    def index(self, data):
        '''Return first index of data in self'''
        for index, value in enumerate(self):
            if value == data:
                return index
        raise ValueError('Could not find {}'.format(data))

    def extend(self, iterator):
        '''Add the elements from iterator to the end of list'''
        for element in iterator:
            self.append(element)

class Linked_list_node(object):
    # pylint: disable=too-few-public-methods

    '''A class to hold one node of a linked list'''

    __slots__ = ['data', 'tail']

    def __init__(self, data, tail):
        self.data = data
        self.tail = tail

    def __str__(self):
        return str(self.data)
