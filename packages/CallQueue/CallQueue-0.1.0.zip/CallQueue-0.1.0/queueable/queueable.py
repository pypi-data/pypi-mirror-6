#!/usr/bin/env python
from collections import defaultdict

import logging


class Queueable(object):
    """Queueable(queue_key)

    Mixin class that allows ojects to share a queue of callable objects. It is
    intended to be mixed into interfaces for database objects.

    Groups of instances can be given their own queues by differentiating
    the queue_key::

        Parent = Queueable( 'family')
        Sister = Queueable('family')
        Brother = Queueable('family')
        Cousin = Queueable('relative')

    The first three objects share a queue, the fourth does not. Loading
    callables by Parent, Sister, or Brother can be executed by calling
    any of their :func:`process_queue` methods, and in doing so any callables
    in the 'relative' queue are untouched.

    This is useful if you have a GUI interface that allows for a command-line
    interface as well. Both sets of interfaces can have their own queue.


    """
    _funcs = defaultdict(list)
    _allow_duplicates = False

    def __init__(self, queue_key):
        self.name = "%s object" % self.__class__.__name__
        self._key = queue_key
        self.q_logger = logging.getLogger('QUEUE')

    def get_allow_duplicates(self):
	"Flag to check if a callable is already in the queue before adding it"
        return self.__class__._allow_duplicates

    def set_allow_duplicates(self, value):
        self.__class__._allow_duplicates = bool(value)

    def get_deny_duplicates(self):
	"Flag to check if a callable is already in the queue before adding it"
        return not self.__class__._allow_duplicates

    def set_deny_duplicates(self, value):
        self.__class__._allow_duplicates = not (bool (value))

    allow_duplicates = property(get_allow_duplicates, set_allow_duplicates)
    deny_duplicates = property(get_deny_duplicates, set_deny_duplicates)

    def queue(self, func, *args, **kwargs):
        """queue(func [, *args, **kwargs])

        Adds the function and arguments to the queue.
        """
        if not self._allow_duplicates:
            if (func, args, kwargs) in self.__class__._funcs[self._key]:
                self.q_logger.debug("%s not queuing up %s to %s (duplicates not allowed",
                    (self.name, func, self._key))
                return False

        if callable(func):
            self.q_logger.debug("%s is queuing up %s to %s" %
                (self.name, func, self._key))
            self.__class__._funcs[self._key].append((func, args, kwargs))
            return True
        else:
            self.q_logger.debug("%s cannot queue non-callable %s",
                self.name, func)
            return False


    def queue_len(self):
        """queue_len(self)

        Returns the length of the queue for this object
        """
        return len(self.__class__._funcs[self._key])

    #todo: It would be nice to be able to recycle these back to the queue
    def do_queue_item(self, nth):
        """do_queue_item(nth)

        Does the nth item in the queue
        """
        try:
            func, args, kwargs = self.__class__._funcs[self._key].pop(nth)
        except IndexError as E:
            self.q_logger.error("%s queue does not have item # %d", self._key, nth)
            raise E

        func(*args, **kwargs)

    def process_queue(self):
        """process_queue

        Calls each function in the Queable objects queue, and clears
        the queue afterward
        """
        self.q_logger.debug("%s is processing queue" % self.name)
        for func, args, kwargs in self.__class__._funcs[self._key]:
            func(*args, **kwargs)
        self.__class__._funcs[self._key] = []
        self.q_logger.debug("%s queue cleared by %s" % (self._key, self.name))


    @classmethod
    def queue_keys(kls):
        """queue_keys()

        Returns a list of all used keys
        """
        return kls._funcs.keys()

    def get_queued_funcs(self):
        """get_queued_funcs()

        Returns a list of all callable objects without arguments
        """
        return [func for func, args, kwargs in self.__class__._funcs[self._key]]

    def get_queue(self):
        """get_queue()

        Returns a list of (callable, args, kwargs) tuples in the queue.
        """
        return [triple for triple in self.__class__._funcs[self._key]]

