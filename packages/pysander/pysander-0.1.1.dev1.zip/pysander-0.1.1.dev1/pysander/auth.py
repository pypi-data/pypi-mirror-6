import context
import repositories

# Base class for all identity objects

class Identity(object):
	def is_root():
		return False

# Derived "root" identity class, represents an identity
# which has access to absolutely everything and can do
# absolutely anything

class RootIdentity(Identity):
	def is_root(self):
		return True

# Derived "user" identity class, represents a user which
# is performing actions against the API

class UserIdentity(Identity):
	def __init__(self, user):
		self.user = user

	def is_root(self):
		return False

# A context base class that can be used
# for constructing a context with an associated identity

class IdentityContext(object):
	def __init__(self):
		self.identity = None

	def get_identity(self):
		return self.identity

	def set_identity(self, identity):
		self.identity = identity

# thrown whenever a user tries to access an unauthorized action

class UnauthorizedError(BaseException):
	pass

# middleware that requires an identity to be authenticated 
# to gain access to its methods

class RequiresAuthMiddleware(object):
	def __init__(self, find=True, query=True, update=True, insert=True, delete=True):
		self._find = find
		self._query = query
		self._update = update
		self._insert = insert
		self._delete = delete

	def throw(self):
		raise UnauthorizedError()

	def find(self, key, next):
		if self.find and context.current().get_identity() is None:
			self.throw()
		return next.find(key)

	def query(self, query, next):
		if self.query and context.current().get_identity() is None:
			self.throw()
		return next.query(query)

	def insert(self, values, next):
		if self.insert and context.current().get_identity() is None:
			self.throw()
		return next.insert(values)

	def update(self, row, changes, next):
		if self.update and context.current().get_identity() is None:
			self.throw()
		return next.update(row, changes)

	def delete(self, key, next):
		if self.delete and context.current().get_identity() is None:
			self.throw()
		return next.delete(key)

# registers a RequiresAuthMiddleware with the provided repository

def require_auth(repository, find=True, query=True, update=True, insert=True, delete=True):
	assert isinstance(repository, repositories.Repository)
	middleware = RequiresAuthMiddleware(find=find, query=query, update=update, insert=insert, delete=delete)
	repository.add_middleware(middleware)