# A single binary filter

class Filter(object):
	def __init__(self, field, op, value):
		self.field = field
		self.op = op
		self.value = value

# A single ordering

class Ordering(object):
	def __init__(self, field, ascending):
		self.field = field
		self.ascending = ascending

# Query logic

class Query(object):
	def __init__(self):
		self.filters = []
		self.orderings = []

	def where(self, field, op, value):
		filter = Filter(field, op, value)
		self.filters.append(filter)
		return self

	def order_by(self, field, ascending):
		ordering = Ordering(field, ascending)
		self.orderings.append(field, ascending)
		return self

def from_json(json):
	query = Query()

	# retrieve the filters from the json
	if 'filters' in json:
		filters = json['filters']
		for filter in filters:
			field = filter['field']
			op = filter['op']
			value = filter['value']
			query.where(field, op, value)

	# retrieve the orderings from the json
	if 'orderings' in json:
		orderings = json['orderings']
		for ordering in orderings:
			field = ordering['field']
			ascending = ordering['ascending']
			query.order_by(field, ascending)

	return query