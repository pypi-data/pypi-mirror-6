# coding: utf-8


__all__  = [
	"BaseDelegate",
	"DelegateMixin"
]


class MissingDelegationType(Exception):
	pass

class WrongDelegation(Exception):
	pass

class DelegateType(type):

	def __init__(cls, name, bases, attrs):
		"""
		Some central control logic later goes in here.
		"""
		pass

class BaseDelegate(object):

	__metaclass__ = DelegateType

class DelegateMixinType(type):

	def __init__(cls, name, bases, attrs):
		# Is this a subclass of DelegateMixin?
		if name != 'DelegateMixin':
			# Does it comform to the Delegate Protocol
			#
			# 1. by specifying a Delegator?
			if not attrs.has_key('delegation_type'):
				raise MissingDelegationType(
					'Subclasses of `DelegateMixin` must specify a `delegation_type`')
			# 2. and the specified Delegator is of DelegateType?
			if not issubclass(attrs['delegation_type'], BaseDelegate):
				raise WrongDelegation('`delegation_type` must be subclasses of BaseDelegate')

class DelegateMixin(object):
	"""
	Inheriting from this Mixin would entail
	the obligations of -

	1. specifying a DelegateType
	2. assert issubclass(self.delegate, self.delegation_type)
	"""

	__metaclass__ = DelegateMixinType

	def delegating(self, action_name, info):
		# Does it have a Delegator anyway?
		if hasattr(self, 'delegate') and (not self.delegate is None):
			if not isinstance(self.delegate, self.delegation_type):
				raise WrongDelegation('Expected `%s`, got `%s` instead' % 
					(self.DelegationType, self.delegate))
			getattr(self.delegate, action_name)(info)