import queries
import sqlalchemy

class SQLContext(object):
	def __init__(self):
		self.sql_connections = {}
		self.sql_transactions = {}
	
	def exit(self, type, value, traceback):
		if value is None:
			print("Committing")
			for k,v in self.sql_transactions.items():
				v.commit()
		else:
			print("Rollback")
			for k,v in self.sql_transactions.items():
				v.rollback()
		self.sql_transactions = {}
		self.sql_connections = {}

	def get_sql_connection(self, engine):
		if engine.url not in self.sql_connections:
			self.sql_connections[engine.url] = engine.connect()
		return self.sql_connections[engine.url]

	def get_sql_transaction(self, engine):
		conn = None
		trans = None
		if engine.url not in self.sql_transactions:
			conn = self.get_sql_connection(engine)
			trans = conn.begin()
			self.sql_transactions[engine.url] = trans
		return conn, trans

# Applies the options of a queries.Query instance
# to a SQLAlchemy select object

def apply_query_options(op, table, query):
	op = apply_query_filters(op, table, query.filters)
	op = apply_query_orderings(op, table, query.orderings)
	return op

# Applies a list of query.Filter objects
# to a SQLAlchemy select object

def apply_query_filters(op, table, filters):
	for filter in filters:
		op = apply_query_filter(op, table, filter)
	return op

# Applies a queries.Filter instance to a SQLAlchemy
# select object

def apply_query_filter(op, table, filter):
	if filter.field not in table.c:
		return op

	str_op = filter.op.upper()
	if str_op == '=':
		return op.where(table.c[filter.field] == filter.value)
	elif str_op == '>':
		return op.where(table.c[filter.field] > filter.value)
	elif str_op == '>=':
		return op.where(table.c[filter.field] >= filter.value)
	elif str_op == '<':
		return op.where(table.c[filter.field] < filter.value)
	elif str_op == '<=':
		return op.where(table.c[filter.field] <= filter.value)
	elif str_op == 'LIKE':
		return op.where(table.c[filter.field].like(filter.value))
	elif str_op == 'IN':
		return op.where(table.c[filter.field].in_(filter.value))

# Applies the orderings of a queries.Query instance
# to a SQLAlchemy select object

def apply_query_orderings(op, table, orderings):
	for ordering in orderings:
		op = apply_query_ordering(op, table, ordering)
	return op

# Applies a queries.Ordering instance to a SQLAlchemy
# select object

def apply_query_ordering(op, table, ordering):
	if ordering.field not in table.c:
		return op
	
	if ordering.ascending:
		return op.order_by(table.c[ordering.field])
	else:
		return op.order_by(sqlalchemy.desc(table.c[ordering.field]))