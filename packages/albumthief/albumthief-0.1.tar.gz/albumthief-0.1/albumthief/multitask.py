# coding: utf-8

from gevent.pool import Pool


def multi_task(handler, targets, concurrency=10):
	"""
	:param handler:		The function to call with
	:type handler:		Callable

	:param targets:		The iterable to run handler on
	:type targets:		Iterable

	:param concurrency:	The concurrency size
	:type concurrency:	IntegerType
	"""
	pool = Pool(concurrency)
	results = pool.map(handler, targets)
	return results