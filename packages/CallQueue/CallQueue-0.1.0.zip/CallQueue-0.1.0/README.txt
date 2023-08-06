==========
Call Queue
==========

Call Queue provides a mixin class to store functions, methods, or any callable object
with the associated arguments and keyword arguments. 

Each Queuable object has a key, so queues can be separated by need.

It can be used directly::

	#!/usr/bin/env python

	from queueable import Queueable

	Arthur = Queueable('human')

	Trillian = Queuable('human')

	Ford = Queuable('alien')

	Zaphod = Queueable('alien')

	def drink_tea(response):
		print "This stuff {}".format(response)

	Arthur.queue(drink_tea, "tastes filthy") # Nothing happens

	Ford.process_queue() # Nothing happens

	Trillian.process_queue() # runs the queued drink_tea function



