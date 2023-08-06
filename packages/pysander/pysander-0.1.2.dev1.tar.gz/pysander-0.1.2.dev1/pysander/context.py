import inspect
import threading

# Key used to store the pysander context within thread local storage

_tls_key = "pysander_context"
_tls = threading.local()

# Context object which preserves states across
# a single request or session, use multiple
# inheritance to compose a context object for
# your specific use case

class Context(object):
	def __init__(self):
		mro = inspect.getmro(self.__class__)
		for i in range(2, len(mro)):
			if hasattr(mro[i], '__init__'):
				mro[i].__init__(self)

	def __enter__(self):
		setattr(_tls, _tls_key, self)
		mro = inspect.getmro(self.__class__)
		for i in range(2, len(mro)):
			if hasattr(mro[i], 'enter'):
				mro[i].enter(self)

	def __exit__(self, type, value, traceback):
		mro = inspect.getmro(self.__class__)
		for i in range(2, len(mro)):
			if hasattr(mro[i], 'exit'):
				mro[i].exit(self, type, value, traceback)
		setattr(_tls, _tls_key, None)


# Context factory which is used for constructing
# context instance that is usefull for a specific
# application

class ContextFactory(object):
	def __init__(self, types):
		types.insert(0, Context)
		self.type = type('ContextInstance', tuple(types), {})

	def create_context(self):
		return self.type()

# Gets the current context object

def current():
	context = getattr(_tls, _tls_key, None)
	return context