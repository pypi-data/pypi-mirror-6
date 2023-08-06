import context
import queries
import repositories
import sqlalchemy
import sql
import utils

# Implements the repository pattern for a SQL table
# Requires that a primary key is defined on the table

class SQLRepository(repositories.Repository):
	def __init__(self, engine=None, table=None):
		repositories.Repository.__init__(self)
		self.engine = engine
		self.table = table
		self.pk_cols = [c for c in table.columns if c.primary_key]
		self.key = utils.Key([c.name for c in self.pk_cols])

	# used for filtering a sql-alchey operation using the values
	# from a key object that was passed to a repo method
	def _apply_key_query(self, key, op):
		key = self.key.coerce(key)
		query = queries.Query()
		for k,v in key.items():
			query.where(k, '=', v)
		return sql.apply_query_options(op, self.table, query)

	# finds a single object from the database table
	def do_find(self, key):
		conn = context.current().get_sql_connection(self.engine)
		op = sqlalchemy.select([self.table])
		op = self._apply_key_query(key, op)
		result = conn.execute(op)
		row = result.fetchone()
		return None if row is None else dict(row)

	# queries the database table for a set of objects
	def do_query(self, query):
		conn = context.current().get_sql_connection(self.engine)
		op = sqlalchemy.select([self.table])
		op = sql.apply_query_options(op, self.table, query)
		rows = conn.execute(op)
		rows = [dict(row) for row in rows]
		return rows

	# updates a database table row with a set of changes
	def do_update(self, row, changes):
		conn = context.current().get_sql_connection(self.engine)
		op = self.table.update()
		op = self._apply_key_query(row, op)
		op = op.values(changes)
		result = conn.execute(op)
		return result.rowcount

	# inserts a single row into the database table
	def do_insert(self, values):
		conn = context.current.get_sql_connection(self.engine)
		op = self.table.insert().values(values)
		result = conn.execute(op)
			
		ret = values.copy()
		pk_index = 0
		pk_values = result.inserted_primary_key
		for pk_col in self.pk_cols:
			name = pk_col.name
			if name not in values and pk_index < len(pk_values):
				ret[name] = pk_values[pk_index]
				pk_index = pk_index + 1
		return ret

	# deletes a single row from the database table
	def do_delete(self, key):
		conn = context.current.get_sql_connection(self.engine)
		op = self.table.delete()
		op = self._apply_key_query(key, op)
		result = conn.execute(op)
		return result.rowcount