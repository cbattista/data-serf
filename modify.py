#modify.py

import os
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *

@lg_authority.groups('auth')
class modify(object):
        """CherryPy server root"""

        auth = lg_authority.AuthRoot()
        auth__doc = "The object that serves authentication pages"


	@cherrypy.expose
	def index(self, **kwargs):
		u = cherrypy.user.name
		cookie = cherrypy.request.cookie

		output = ""

		if cookie.has_key("datamaster_table"):
			table = cookie["datamaster_table"].value
			datatable = "%s_%s" % (table, u)
			tableName = "%s_%s_vars" % (table, u)	

			posts = mt.MongoAdmin("datamaster").db[tableName].posts


			if kwargs.has_key('set_op'):
				output += self.query(datatable, kwargs)
			if kwargs.has_key('new_var'):
				output += self.create(datatable, kwargs)
			if kwargs.has_key('merge_var'):
				output += self.merge(datatable, kwargs)

	
			keys = posts.find().distinct('name')

			modify = getForm(template.get_def("modify").render(var_options=keys), modify_url)

			create = getForm(template.get_def("create_column").render(var_options=keys), modify_url)

			merge = getForm(template.get_def("merge_column").render(var_options=keys), modify_url)
		else:
			modify = no_table
			create = no_table
			merge = no_table
	
		items = [['create', create], ['merge', merge], ['modify', modify]]

		output += getAccordion(items)

		return getPage(output, "modify", "modify")


	def create(self, table, kwargs):
		posts =mt.MongoAdmin("datamaster").db[table].posts
		var_type = kwargs['new_var_type']
		name = kwargs['new_var']

		if name:
			if kwargs['orig_var']:

				if not kwargs['op']:
					for row in posts.find():
						row[name] = row[kwargs['orig_var']]
						posts.save(row)
				else:
					ot = mt.StringToType(kwargs['op_text'])
					for row in posts.find():
						if kwargs['op'] == '-=':
							row[name] = row[kwargs['orig_var']] - ot
						elif kwargs['op'] == '+=':
							row[name] = row[kwargs['orig_var']] - op
						posts.save(row)
			else:
				posts.update({}, {'$set':{name : 'NA'}})
	
			output = "<div class='alert alert-success'>variable %s created</div>" % name

			#make a note of this new column
			tableName = "%s_vars" % table
			var_posts = mt.MongoAdmin("datamaster").db[tableName].posts
			var_posts.update({'name':name}, {'$set':{'var_type':var_type}}, upsert=True)

		else:
			output = "<div class='alert alert-error'>no columns created</div>"

		return output

	def merge(self, table, kwargs):
		posts =mt.MongoAdmin("datamaster").db[table].posts
		name = kwargs['merge_var']
		op = kwargs['op']
		var_l = kwargs['var_left']
		var_r = kwargs['var_right']
		var_type = kwargs['merge_var_type']

		if var_l and var_r and op:
			if op == "+":
				for row in posts.find():
					row[name] = row[var_l] + row[var_r]
					posts.save(row)
			elif op == "-":
				for row in posts.find():
					row[name] = row[var_l] - row[var_r]
					posts.save(row)
			elif op == "*":
				for row in posts.find():
					row[name] = row[var_l] * row[var_r]
					posts.save(row)
			elif op == "/":
				for row in posts.find():
					row[name] = row[var_l] / row[var_r]
					posts.save(row)
			elif op == "join text":
				for row in posts.find():
					row[name] = str(row[var_l]) + "_" + str(row[var_r])
					posts.save(row)
					
			#make a note of this new column
			tableName = "%s_vars" % table
			var_posts = mt.MongoAdmin("datamaster").db[tableName].posts
			var_posts.update({'name':name}, {'$set':{'var_type':var_type}}, upsert=True)
			output = "<div class='alert alert-success'>new variable %s created from %s and %s</div>" % (name, var_l, var_r)
		else:
			output = "<div class='alert alert-error'>no merge performed</div"

		return output

	def query(self, table, kwargs):
		posts = mt.MongoAdmin("datamaster").db[table].posts

		qdict={}
		qdict['>='] = '$gte'
		qdict['>'] = '$gt'
		qdict['<='] = '$lte'
		qdict['<'] = '$lt'

		#get the condition
		if kwargs['if_text']:
			if_val = mt.StringToType(kwargs['if_text'])
			if kwargs['if'] == '==':
				condition = {kwargs['if_var'] : if_val}
			else:
				subcond = {qdict[kwargs['if']] : if_val}
				condition = {kwargs['if_var'] : subcond}

		else:
			condition = {}

		query = {}

		print kwargs.keys()

		if kwargs['set_text'] and kwargs['set_op']:
			st = mt.StringToType(kwargs['set_text'])
			if kwargs['set_op'] == '=':
				query = {'$set' : {kwargs['set_col'] : st}}
			elif kwargs['set_op'] == '+=':
				query = { '$inc': { kwargs['set_col']: st}}
			elif kwargs['set_op'] == '-=':
				query = { '$inc': { kwargs['set_col']: -st}}
		print kwargs		

		print condition, query

		if query:
			posts.update(condition, query, multi=True)
			return "<div class='alert alert-success'>variable %s was modified, condition: %s  command: %s</div>" % (kwargs['set_col'], condition, query)
		else:
			return "<div class='alert alert-error'>no modifications</div>"
		


if __name__ == '__main__':
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':modify_port,})
	cherrypy.quickstart(modify())
