# Middleware, which can extended to wrap repository operations

class RepositoryMiddleware(object):
	def find(self, key, next):
		return next.find(key)

	def query(self, query, next):
		return next.query(query)

	def insert(self, values, next):
		return next.insert(values)

	def update(self, row, changes, next):
		return next.update(row, changes)

	def delete(self, key, next):
		return next.delete(key)

# Hacky, a single object that can be used as the next argument
# to every registered middleware for any database operation

class MiddlewareIterator(object):
	def __init__(self, repository):
		self.index = -1
		self.repository = repository

	def _next_middleware(self):
		self.index = self.index + 1
		middlewares = self.repository.middleware
		if self.index < len(middlewares):
			return middlewares[self.index]
		else:
			return None

	def find(self, key):
		middleware = self._next_middleware()
		if middleware is not None:
			return middleware.find(key, self)
		else:
			return self.repository.do_find(key)

	def query(self, query):
		middleware = self._next_middleware()
		if middleware is not None:
			return middleware.query(query, self)
		else:
			return self.repository.do_query(query)


	def insert(self, values):
		middleware = self._next_middleware()
		if middleware is not None:
			return middleware.insert(values, self)
		else:
			return self.repository.do_insert(values)

	def update(self, row, changes):
		middleware = self._next_middleware()
		if middleware is not None:
			return middleware.update(row, changes, self)
		else:
			return self.repository.do_update(row, changes)

	def delete(self, key):
		middleware = self._next_middleware()
		if middleware is not None:
			return middleware.delete(ke, self)
		else:
			return self.repository.do_delete(key)

# Base repository class, should be extended with specific
# logic for repositories

class Repository(object):
	def __init__(self):
		self.middleware = []

	def add_middleware(self, middleware):
		self.middleware.insert(0, middleware)

	def do_find(self, key):
		raise Exception('do_find is not implemented')

	def do_query(self, query):
		raise Exception('do_query is not implemented')

	def do_insert(self, values):
		raise Exception('do_insert is not implemented')

	def do_update(self, key, changes):
		raise Exception('do_update is not implemented')

	def do_delete(self, key):
		raise Exception('do_delete is not implemented')

	def find(self, key):
		iterator = MiddlewareIterator(self)
		return iterator.find(key)

	def query(self, query):
		iterator = MiddlewareIterator(self)
		return iterator.query(query)

	def insert(self, values):
		iterator = MiddlewareIterator(self)
		return iterator.insert(values)

	def update(self, key, changes):
		row = self.find(key)
		iterator = MiddlewareIterator(self)
		return iterator.update(row, changes)

	def delete(self, key):
		iterator = MiddlewareIterator(self)
		return iterator.delete(key)