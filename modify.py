#modify.py

import os
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *

@lg_authority.groups('auth')
class modify(object):

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

			preview = self.preview(datatable, tableName, kwargs)

			if kwargs.has_key('set_op'):
				output += self.query(datatable, kwargs)
			if kwargs.has_key('new_var'):
				output += self.create(datatable, kwargs)
			if kwargs.has_key('merge_var'):
				output += self.merge(datatable, kwargs)

	
			keys = posts.find().distinct('name')

			condition = getCondition(var_options=keys, label='If (optional)')
			setter = getSetter(var_options=keys, label='Set (required)')

			modify = getForm(condition + setter, modify_url, legend='transform a variable')

			create = getForm(template.get_def("create_column").render(var_options=keys), modify_url)

			merge = getForm(template.get_def("merge_column").render(var_options=keys), modify_url)
		else:
			modify = no_table
			create = no_table
			merge = no_table
			preview = no_table

		items = [['create', create], ['merge', merge], ['modify', modify], ['preview', preview]]

		output += getAccordion(items, contentID='modify-small')

		return getPage(output, "modify", "modify")

	def preview(self, table, var_table, kwargs):

		dm = mt.MongoAdmin("datamaster")

		VARs = mt.MongoAdmin("datamaster").db[var_table].posts

		sid = VARs.find_one({'var_type': 'subject'})['name']
		trial = VARs.find_one({'var_type': 'trial'})['name']
		IVs = VARs.find({'var_type': 'IV'}).distinct('name')
		DVs = VARs.find({'var_type': 'DV'}).distinct('name')
		sids = dm.db[table].posts.find().distinct(sid)
		
		if kwargs.has_key('op-preview'):
			sub = int(kwargs['op-preview'])
		else:
			sub = sids[0]

		lines = dm.write(table, {sid:sub}, headers = [sid, trial] + IVs + DVs, sort=trial, output="list")
		table = getTable(lines, 'Subject %s' % sub)


		output = "<p>If you just modified your data you might need to <a class='btn' href=%s>refresh the preview</a> to see the changes you just made.</p>" % modify_url
		output += "<p>or switch the participant to:</p>" 
		output += getForm(getOptions(sids, ID="preview", active=sub), form_action=modify_url)
		output += table

		return output


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
	
			output = getAlert("variable %s created" % name, "good")

			#make a note of this new column
			tableName = "%s_vars" % table
			var_posts = mt.MongoAdmin("datamaster").db[tableName].posts
			var_posts.update({'name':name}, {'$set':{'var_type':var_type}}, upsert=True)

		else:
			output = getAlert("no columns created")

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

		condition = parseCondition(kwargs)

		set_text = kwargs['set_text']
		set_val = kwargs['set_val']
		set_op = kwargs['set_op']
		set_col = kwargs['set_col']

		if (set_text or set_val) and set_op:

			if set_val:
				for row in posts.find(condition):
					print set_col, row.has_key(set_col), set_val, row.has_key(set_val)
					if row.has_key(set_val):
						if set_op == '=':
							print set_col, set_val
							row[set_col] = row[set_val]
							posts.save(row)
						elif set_op == '+=':
							if row.has_key(set_col):
								row[set_col] += row[set_val]
								posts.save(row)
						elif set_op == '-=':
							if row.has_key(set_col):
								row[set_col] -= row[set_val]
								posts.save(row)

				query = "set %s %s %s" % (set_col, set_op, set_val)

			else:
				
				query = {}

				st = mt.StringToType(kwargs['set_text'])

				if kwargs['set_op'] == '=':
					query = {'$set' : {kwargs['set_col'] : st}}
				elif kwargs['set_op'] == '+=':
					query = { '$inc': { kwargs['set_col']: st}}
				elif kwargs['set_op'] == '-=':
					query = { '$inc': { kwargs['set_col']: -st}}

				posts.update(condition, query, multi=True)

			text = "variable %s was modified, condition: %s  command: %s" % (kwargs['set_col'], condition, query)
			return getAlert(text, "good")

		else:
			return getAlert("No modifications made")
		


if __name__ == '__main__':
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':modify_port,})
	cherrypy.quickstart(modify())
