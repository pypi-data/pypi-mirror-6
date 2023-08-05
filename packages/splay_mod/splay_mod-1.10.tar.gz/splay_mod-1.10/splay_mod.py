#!/usr/bin/python



'''
Module implementing splay trees.
Adapted to DRS' coding style from http://code.google.com/p/pysplay/downloads/detail?name=pysplay-1.0.zip&can=2&q=

http://en.wikipedia.org/wiki/Splay_tree
'''

import math

# Future directions:
# 1) It might be nice to have remove_min and remove_max
# 2) It might be nice to have an iterator or generator for the tree as a whole - something that would work
#    without rearranging the tree probably
# 3) It might be nice to have a __str__ method
# 4) It might be nice to have a depth method
# 5) It might be nice to have a __len__ method

def center(string, field_use_width, field_avail_width):
    '''Center a string within a given field width'''
    field_use = (string + '_' * (field_use_width - 1))[:field_use_width - 1]
    pad_width = (field_avail_width - len(field_use)) / 2.0
    result = ' ' * int(pad_width) + field_use + ' ' * int(math.ceil(pad_width))
    return result

class Node(object):
    # pylint: disable=R0903
    # R0903: We're pretty much just a container; we don't need a lot of public methods
    '''An individual node of a splay tree'''
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

    def inorder_traversal(self, visit):
        '''Do an inorder traversal - without lots of parameters'''
        if self.left != None:
            self.left.inorder_traversal(visit)
        visit(self.key, self.value)
        if self.right != None:
            self.right.inorder_traversal(visit)

    def detailed_inorder_traversal(self, visit, depth=0, from_left=0):
        '''Do an inorder traversal - with lots of parameters'''
        if self.left != None:
            self.left.detailed_inorder_traversal(visit, depth + 1, from_left * 2)
        visit(self, self.key, self.value, depth, from_left)
        if self.right != None:
            self.right.detailed_inorder_traversal(visit, depth + 1, from_left * 2 + 1)

    def __str__(self):
        return '%s/%s' % (self.key, self.value)


class Splay(object):
    '''An entire splay tree'''
    def __init__(self):
        self.root = None
        self.header = Node(None, None) #For splay()

    def insert(self, key, value):
        '''Insert a key into the splay tree'''
        if (self.root is None):
            self.root = Node(key, value)
            return

        self.splay(key)
        if self.root.key == key:
            # If the key is already there in the tree, don't do anything.
            return

        node = Node(key, value)
        if key < self.root.key:
            node.left = self.root.left
            node.right = self.root
            self.root.left = None
        else:
            node.right = self.root.right
            node.left = self.root
            self.root.right = None
        self.root = node

    __setitem__ = insert

    def remove(self, key):
        '''Remove a node from this splay tree'''
        self.splay(key)
        if key != self.root.key:
            raise ValueError('key not found in tree')

        # Now delete the root.
        if self.root.left is None:
            self.root = self.root.right
        else:
            prior_right = self.root.right
            self.root = self.root.left
            self.splay(key)
            self.root.right = prior_right

    def find_min(self):
        '''Find the minimum key in the splay tree'''
        if self.root is None:
            raise ValueError
        candidate = self.root
        while candidate.left != None:
            candidate = candidate.left
        self.splay(candidate.key)
        return candidate.key

    def find_max(self):
        '''Find the maximum key in the splay tree'''
        if self.root is None:
            raise ValueError
        candidate = self.root
        while (candidate.right != None):
            candidate = candidate.right
        self.splay(candidate.key)
        return candidate.key

    def find(self, key):
        '''Look up a value (not key) in the splay tree by key'''
        if self.root is None:
            raise ValueError
        self.splay(key)
        if self.root.key != key:
            raise ValueError
        return self.root.value

    __getitem__ = find

    def __bool__(self):
        '''Test whether the splay tree is empty'''
        if self.root is None:
            return False
        else:
            return True

    def __nonzero__(self):
        '''Same as __bool__'''
        return self.__bool__()

    def splay(self, key):
        '''
        "splay" the tree
        http://en.wikipedia.org/wiki/Splay_tree
        '''

        left = self.header
        right = self.header
        subtree = self.root
        self.header.left = None
        self.header.right = None

        while True:
            if key < subtree.key:
                if subtree.left is None:
                    break
                if key < subtree.left.key:
                    prior_left = subtree.left
                    subtree.left = prior_left.right
                    prior_left.right = subtree
                    subtree = prior_left
                    if subtree.left is None:
                        break
                right.left = subtree
                right = subtree
                subtree = subtree.left
            elif key > subtree.key:
                if subtree.right is None:
                    break
                if key > subtree.right.key:
                    prior_right = subtree.right
                    subtree.right = prior_right.left
                    prior_right.left = subtree
                    subtree = prior_right
                    if subtree.right is None:
                        break
                left.right = subtree
                left = subtree
                subtree = subtree.right
            else:
                break
        left.right = subtree.left
        right.left = subtree.right
        subtree.left = self.header.right
        subtree.right = self.header.left
        self.root = subtree

    def inorder_traversal(self, visit):
        '''Traverse a tree, visiting each node as we go'''
        self.root.inorder_traversal(visit)

    def detailed_inorder_traversal(self, visit):
        '''Traverse a tree, visiting each node as we go, with extra visit parameters'''
        self.root.detailed_inorder_traversal(visit, depth=0, from_left=0)

    def depth(self):
        '''Return the depth of the splay (tree)'''

        class maxer(object):
            '''Class facilitates computing the maximum depth of all the splay (tree) branches'''
            def __init__(self, maximum=-1):
                self.max = maximum

            def feed(self, node, key, value, depth, from_left):
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                '''Check our maximum so far against the current node - updating as needed'''
                dummy = node
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.max:
                    self.max = depth

            def result(self):
                '''Return the maximum we've found - plus one for human readability'''
                return self.max + 1

        max_obj = maxer()
        self.detailed_inorder_traversal(max_obj.feed)
        return max_obj.result()

    def _depth_and_field_width(self):
        '''Compute the depth of the tree and the maximum width within the nodes - for pretty printing'''
        class maxer(object):
            '''Class facilitates computing the max depth of the splay (tree) and max width of the nodes'''
            def __init__(self, maximum=-1):
                self.depth_max = maximum
                self.field_width_max = -1

            def feed(self, node, key, value, depth, from_left):
                '''Check our maximums so far against the current node - updating as needed'''
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.depth_max:
                    self.depth_max = depth
                str_node = str(node)
                len_key = len(str_node)
                if len_key > self.field_width_max:
                    self.field_width_max = len_key

            def result(self):
                '''Return the maximums we've computed'''
                return (self.depth_max + 1, self.field_width_max)

        max_obj = maxer()
        self.detailed_inorder_traversal(max_obj.feed)
        return max_obj.result()

    def __str__(self):
        '''Format a splay tree as a string'''
        class Desc(object):
            # pylint: disable=R0903
            # R0903: We don't need a lot of public methods
            '''Build a pretty-print string during a recursive traversal'''
            def __init__(self, pretree):
                self.tree = pretree

            def update(self, node, key, value, depth, from_left):
                '''Add a node to the tree'''
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                dummy = key
                dummy = value
                self.tree[depth][from_left] = str(node)

        if self.root is None:
            # empty output for an empty tree
            return ''
        else:
            pretree = []
            depth, field_use_width = self._depth_and_field_width()
            field_use_width += 1
            for level in range(depth):
                string = '_' * (field_use_width - 1)
                pretree.append([ string ] * 2 ** level)
            desc = Desc(pretree)
            self.root.detailed_inorder_traversal(desc.update)
            result = []
            widest = 2 ** (depth - 1) * field_use_width
            for level in range(depth):
                two_level = 2 ** level
                field_avail_width = widest / two_level
                string = ''.join([ center(x, field_use_width, field_avail_width) for x in desc.tree[level] ])
                # this really isn't useful for more than dozen values or so, and that without priorities printed
                result.append(('%2d ' % level) + string)
            return '\n'.join(result)

    class state_class(object):
        # pylint: disable=R0903
        # R0903: We don't need a lot of public methods
        '''A state class, used for iterating over the nodes in a splay'''
        def __init__(self, todo, node):
            self.todo = todo
            self.node = node

        def __repr__(self):
            return '%s %s' % (self.todo, self.node)



    # These three things: keys, values, items; are a bit of a cheat.  In Python 2, they're really supposed to return lists,
    # but we return iterators like python 3.  A better implementation would check what version of python we're targetting,
    # give this behavior for python 3, and coerce the value returned to a list for python 2.
    def iterkeys(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [ self.state_class('L', self.root) ]

        while stack:
            state = stack.pop()
            if state.node != None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key
                else:
                    if state.node.right != None:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left != None:
                        stack.append(self.state_class('L', state.node.left))

    keys = iterator = __iter__ = iterkeys

    def itervalues(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [ self.state_class('L', self.root) ]

        while stack:
            state = stack.pop()
            if state.node != None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.value
                else:
                    if state.node.right != None:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left != None:
                        stack.append(self.state_class('L', state.node.left))

    values = itervalues

    def iteritems(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [ self.state_class('L', self.root) ]

        while stack:
            state = stack.pop()
            if state.node != None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key, state.node.value
                else:
                    if state.node.right != None:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left != None:
                        stack.append(self.state_class('L', state.node.left))

    items = iteritems

    def reverse_iterator(self):
        '''Iterate over the nodes of the splay in reverse order'''
        stack = [ self.state_class('L', self.root) ]

        while stack:
            state = stack.pop()
            if state.node != None:
                if state.todo == 'V':
                    yield state.node.key
                else:
                    if state.node.left != None:
                        stack.append(self.state_class('L', state.node.left))
                    stack.append(self.state_class('V', state.node))
                    if state.node.right != None:
                        stack.append(self.state_class('R', state.node.right))
