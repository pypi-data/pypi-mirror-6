
class Key(object):
	def __init__(self, fields):
		self.fields = fields

	def count(self):
		return len(self.fields)

	def coerce(self, key):
		if not isinstance(key, dict):
			temp = {}
			temp[self.fields[0]] = key
			key = temp

		copy = {}
		for field in self.fields:
			if field not in key or key[field] is None:
				raise Exception('could not coerce key')
			copy[field] = key[field]
			
		return copy

