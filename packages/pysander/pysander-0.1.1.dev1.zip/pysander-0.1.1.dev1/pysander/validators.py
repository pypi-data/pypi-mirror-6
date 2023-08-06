import re
import validation

# Checks for values that are required

class RequiredValidator(validation.Validator):
	def __init__(self, code):
		validation.Validator.__init__(self, code)

	def validate(self, value, changeset=False, present=False):
		if (present or not changeset) and value == None:
			self.throw()
		return value


# Checks for an accessible foreign key value

class ForeignKeyValidator(validation.Validator):
	def __init__(self, code, repository):
		validation.Validator.__init__(self, code)
		self.repository = repository

	def validate(self, value, changeset=False, present=False):
		if present:
			fk = self.repository.find(value)
			if fk is None:
				self.throw()
		return value

# Checks for an integer value

class IntegerValidator(validation.Validator):
	def __init__(self, code, convert=False, min=None, max=None):
		validation.Validator.__init__(self, code)
		self.convert = convert
		self.min = min
		self.max = max

	def validate(self, value, changeset=False, present=False):
		if present:
			if not isinstance(value, int):
				if self.convert:
					try:
						value = int(str(value), 10)
					except ValueError:
						self.throw()
				else:
					self.throw()

			if self.min != None and value < self.min:
				self.throw()
			elif self.max != None and value > self.max:
				self.throw()
		return value

# Checks for a string value

class StringValidator(validation.Validator):
	def __init__(self, code, convert=False, min_length=None, max_length=None):
		validation.Validator.__init__(self, code)
		self.convert = convert
		self.min_length = min_length
		self.max_length = max_length

	def validate(self, value, changeset=False, present=False):
		if present:
			if not isinstance(value, str):
				if self.convert:
					try:
						value = str(value)
					except ValueError:
						self.throw()
				else:
					self.throw()

			if self.min_length != None and len(value) < self.min_length:
				self.throw()
			elif self.max_length != None and len(value) > self.max_length:
				self.throw()
		return value

# Checks for a valid email address

class EmailAddressValidator(validation.Validator):
	def __init__(self, code):
		validation.Validator.__init__(self, code)
	
	def validate(self, value, changeset=False, present=False):
		if present:
			if re.match("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$", value, re.IGNORECASE) == None:
				self.throw()
		return value

# construction helpers

def required(code):
	return RequiredValidator(code)

def foreign_key(code, repository):
	return ForeignKeyValidator(code, repository)

def integer(code, convert=False, min=None, max=None):
	return IntegerValidator(code, convert=convert, min=min, max=max)

def string(code, convert=False, min_length=None, max_length=None):
	return StringValidator(code, convert=convert, min_length=min_length, max_length=max_length)

def email_address(code):
	return EmailAddressValidator(code)