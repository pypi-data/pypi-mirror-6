import context
import queries
import repositories
import sql
import utils
import datetime
import sqlalchemy
from sqlalchemy.sql.expression import literal_column, bindparam

# Implements the repository pattern for audited SQL tables

class SQLAuditRepository(repositories.Repository):
	def __init__(self, engine=None, table=None, content_table=None, revision_column='revision', created_at_column='created_at', deleted_at_column='deleted_at', updated_at_column='at'):
		repositories.Repository.__init__(self)
		self.engine = engine
		self.table = table
		self.content_table = content_table
		self.revision_column = revision_column
		self.created_at_column = created_at_column
		self.deleted_at_column = deleted_at_column
		self.updated_at_column = updated_at_column
		self.pk_cols = [c for c in table.columns if c.primary_key]
		self.key = utils.Key([ c.name for c in self.pk_cols ])	

		for pk_col in self.pk_cols:
			assert pk_col.name in self.content_table.c
		# deleted_at is necessary to know which objects exist right now
		# the others (updated_at,created_at) are not strictly necessary
		assert deleted_at_column is not None

		self.snapshot_table = self._build_snapshot_table()

	def _build_snapshot_table(self):
		columns = [c for c in self.content_table.columns]
		if self.created_at_column is not None:
			columns.append(self.table.c[self.created_at_column])

		# create the appropriate filters
		op = sqlalchemy.select(columns)
		for col in self.pk_cols:
			op = op.where(self.table.c[col.name] == self.content_table.c[col.name])
		op = op.where(self.table.c[self.revision_column] == self.content_table.c[self.revision_column])
		op = op.where(self.table.c[self.deleted_at_column] == None)
		return op.alias(self.table.name + '_snapshot')

	# used for filtering a sql-alchemy operation using the values
	# from a key object that was passed to a repo method
	def _apply_key_query(self, key, table, op):
		key = self.key.coerce(key)
		query = queries.Query()
		for k,v in key.items():
			query.where(k, '=', v)
		return sql.apply_query_options(op, table, query)


	def do_find(self, key):
		conn = context.current().get_sql_connection(self.engine)
		op = sqlalchemy.select([self.snapshot_table])
		op = self._apply_key_query(key, self.snapshot_table, op)
		result = conn.execute(op)
		row = result.fetchone()
		return None if row is None else dict(row)

	def do_query(self, query):
		conn = context.current().get_sql_connection(self.engine)
		op = sqlalchemy.select([self.snapshot_table])
		op = sql.apply_query_options(op, self.snapshot_table, query)
		rows = conn.execute(op)
		rows = [dict(row) for row in rows]
		return rows

	def do_update(self, row, changes):
		key = self.key.coerce(row)
		conn,trans = context.current().get_sql_transaction(self.engine)
			
		get_op = sqlalchemy.select([self.table])
		get_op = self._apply_key_query(key, self.table, get_op)
		result = conn.execute(get_op)
		main_row = dict(result.fetchone())
		old_revision = main_row[self.revision_column]
		new_revision = old_revision + 1

		up_rev_values = {}
		up_rev_values[self.revision_column] = new_revision
		up_rev_op = self.table.update()
		up_rev_op = self._apply_key_query(row, self.table, up_rev_op)
		up_rev_op = up_rev_op.values(up_rev_values)
		result = conn.execute(up_rev_op)
				
		rev_select_cols = []
		for col in self.content_table.columns:
			if col.name == self.updated_at_column:
				rev_select_cols.append(bindparam("now", value=datetime.datetime.now()).label(col.name))
			elif col.name == self.revision_column:
				rev_select_cols.append(bindparam("new_revision", value=new_revision).label(col.name))
			elif col.name in changes:
				rev_select_cols.append(bindparam(col.name + "_val", value=changes[col.name]).label(col.name))
			else:
				rev_select_cols.append(col)

		rev_select_op = sqlalchemy.select(rev_select_cols)
		rev_select_op = self._apply_key_query(key, self.content_table, rev_select_op)
		rev_select_op = rev_select_op.where(self.content_table.c[self.revision_column] == old_revision)
		rev_insert_op = self.content_table.insert().from_select([c.name for c in self.content_table.columns], rev_select_op)
		result = conn.execute(rev_insert_op)

	def do_insert(self, values):
		content_row = None
		conn,trans = context.current().get_sql_transaction(self.engine)
		now = datetime.datetime.now()
		main_row = {}
		main_row[self.revision_column] = 1
		main_row[self.deleted_at_column] = None
		if self.created_at_column != None:
			main_row[self.created_at_column] = now

		main_ins_op = self.table.insert()
		main_ins_op = main_ins_op.values(main_row)
		result = conn.execute(main_ins_op)

		content_row = values.copy()
		content_row[self.revision_column] = 1
		if self.updated_at_column != None:
			content_row[self.updated_at_column] = now

		pk_index = 0
		pk_values = result.inserted_primary_key
		for pk_col in self.pk_cols:
			name = pk_col.name
			if name not in values and pk_index < len(pk_values):
				content_row[name] = pk_values[pk_index]
				pk_index = pk_index + 1

		content_ins_op = self.content_table.insert()
		content_ins_op = content_ins_op.values(content_row)
		result = conn.execute(content_ins_op)
		return self.key.coerce(content_row)

	def do_delete(self, key):
		conn, trans = context.current.get_sql_connection(self.engine)
		changes = {}
		changes[self.deleted_at_column] = datetime.datetime.now()
		op = self.table.update()
		op = self.table.values(changes)
		result = conn.execute(op)