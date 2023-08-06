import flask
import auth
import context
import queries
import json
import validation

# Context extension that adds http requests to the pysander context object

class HTTPContext(object):
	def __init__(self):
		self.request = None

	def enter(self):
		self.request = flask.request

	def get_request(self):
		return self.request

# Used for hosting repositories within a flask application
# and mapping HTTP requests to repository methods

class HostedRepository(object):
	def __init__(self, repository, context_factory):
		self.repository = repository
		self.context_factory = context_factory

	def do(self, action):
		try:
			with self.context_factory.create_context():
				return action()
		except validation.ValidationError as e:
			return e.codes, 401
		except auth.UnauthorizedError as e:
			return "Unauthorized Access", 403

	def do_find(self, id):
		row = self.repository.find(id)
		if row is not None:
			return flask.jsonify(row)
		else:
			return flask.make_response('Not found', 404)

	def do_query(self):
		json = context.current().get_request.get_json()
		query = queries.from_json(json)
		rows = self.repository.query(query)
		return flask.jsonify(rows)

	def do_insert(self):
		json = context.current().get_request().get_json()
		key = self.repository.insert(json)
		return flask.jsonify(self.repository.find(key))

	def do_update(self, id):
		json = context.current().get_request().get_json()
		result = self.repository.update(id, json)
		return flask.jsonify(self.repository.find(id))

	def do_delete(self, id):
		result = self.repository.delete(id)
		return flask.jsonify(result)

	def find(self, id):
		return self.do(lambda: self.do_find(id))

	def query(self):
		return self.do(lambda: self.do_query())

	def insert(self):
		return self.do(lambda: self.do_insert())

	def update(self, id):
		return self.do(lambda: self.do_update(id))

	def delete(self, id):
		return self.do(lambda: self.do_delete(id))

# Adds a repository to a flask application

def host_repository(app, name, repository, context_factory):
	resource_url = '/' + name + '/<id>'
	insert_url = '/' + name + '/'
	query_url = '/' + name + '/query'

	hosted = HostedRepository(repository, context_factory)
	app.add_url_rule(resource_url, name + '_find', hosted.find, methods=['GET'] )
	app.add_url_rule(resource_url, name + '_update', hosted.update, methods=['PATCH'] )
	app.add_url_rule(resource_url, name + '_delete', hosted.delete, methods=['DELETE'] )
	app.add_url_rule(insert_url, name + '_insert', hosted.insert, methods=['POST'] )
	app.add_url_rule(query_url, name + '_query', hosted.query, methods=['GET'] )