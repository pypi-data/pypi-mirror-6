import repositories

# Exception thrown whenever a validation error occurs

class ValidationError(BaseException):
	def __init__(self, codes):
		self.codes = codes

# Base class for all validators

class Validator(object):
	def __init__(self, code):
		self.code = code

	def throw(self):
		raise ValidationError([self.code])

	def validate(self, value, changeset=False):
		return True

# A set of validators for a single field

class Field(object):
	def __init__(self, name):
		self.name = name
		self.validators = []

	def add_validator(self, validator):
		self.validators.append(validator)

	def validate(self, row, changeset=False):
		value = None
		present = False
		if self.name in row:
			value = row[self.name]
			present = True

		for validator in self.validators:
			value = validator.validate(value,changeset=changeset,present=present)

		if value != None:
			row[self.name] = value

# A set of validators that can be applied to a repository

class ValidatorSet(object):
	def __init__(self):
		self.fields = {}

	def add_validator(self, field, validator):
		if field not in self.fields:
			self.fields[field] = Field(field)
		self.fields[field].add_validator(validator)

	def validate(self, row, changeset=False):
		codes = []
		for name,field in self.fields.items():
			try:
				field.validate(row, changeset=changeset)
			except ValidationError as e:
				codes += e.codes
		if len(codes) > 0:
			raise ValidationError(codes)

# Validation middleware for wrapping a repository

class ValidatorMiddleware(repositories.RepositoryMiddleware):
	def __init__(self, set):
		self.set = set

	def insert(self, values, next):
		self.set.validate(values, changeset=False)
		return next.insert(values)

	def update(self, row, changes, next):
		self.set.validate(changes, changeset=True)
		return next.update(row, changes)

# Adds validation to a repository

def add_validation(repo, validators):
	assert isinstance(repo, repositories.Repository)
	assert isinstance(validators, dict)

	middleware = None
	set = ValidatorSet()
	for k,v in validators.items():
		if not isinstance(v, list):
			v = [v]
		for validator in v:
			set.add_validator(k, validator)

	middleware = ValidatorMiddleware(set)
	repo.add_middleware(middleware)
