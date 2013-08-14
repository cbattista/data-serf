#modify.py

import os
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *
import common

@lg_authority.groups('auth')
class modify(object):

	@cherrypy.expose
	def index(self, **kwargs):
		u = cherrypy.user.name

		output = ""

		t = common.getCookie('datamaster_table')

		#select any tables
		if kwargs.has_key('select_table'):
			t = kwargs['select_table']
			common.setCookie('datamaster_table', t)

		if t:
			table = "%s_%s" % (t, u)
			var_table = "%s_%s_vars" % (t, u)	

			posts = mt.MongoAdmin("datamaster").db[var_table].posts

			if kwargs.has_key('set_op'):
				output += self.query(table, kwargs)
			if kwargs.has_key('new_var'):
				output += self.create(table, kwargs)
			if kwargs.has_key('merge_var'):
				output += self.merge(table, kwargs)

	
			keys = posts.find().distinct('name')

			condition = getCondition(var_options=keys, label='If (optional)')
			setter = getSetter(var_options=keys, label='Set (required)')

			modify = getForm(condition + setter, modify_url, legend='transform a variable')

			create = getForm(template.get_def("create_column").render(var_options=keys), modify_url)

			merge = getForm(template.get_def("merge_column").render(var_options=keys), modify_url)

			preview = self.preview(table, kwargs)


		else:
			modify = no_table
			create = no_table
			merge = no_table
			preview = no_table

		items = [['select table', select_table(modify_url, t)], ['create', create], ['merge', merge], ['modify', modify], ['preview', preview]]

		output += getAccordion(items, contentID='modify-small')

		return getPage(output, "modify", "modify")

	def preview(self, table, kwargs):

		dm = mt.MongoAdmin("datamaster")

		sid, trial, IVs, DVs, sids, run = common.getVariables(table, sids=True)

		output = ""

		if sid and trial and (IVs or DVs):
			if kwargs.has_key('op-preview'):
				sub = kwargs['op-preview']
				try:
					sub = int(sub)
				except:
					pass
			else:
				sub = sids[0]

			lines = dm.write(table, {sid:sub}, headers = [sid, trial] + IVs + DVs, sort=trial, output="list")
			table = getTable(lines, 'Subject %s' % sub)
			output += "<p>If you just modified your data you might need to <a class='btn' href=%s>refresh the preview</a> to see the changes you just made.</p>" % modify_url
			output += "<p>or switch the participant to:</p>" 
			output += getForm(getOptions(sids, ID="preview", active=sub), form_action=modify_url)
			output += table
		else:
			output += "<p>You do not have all the necessary variables selected.  Better <a class='btn' href='%s'>choose some variables</a>, m'lord.</p>" % manage_url

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

			common.activity_log("modify", "create", table, kwargs)

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
					
			common.activity_log("modify", "merge", table, kwargs)

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

			common.activity_log("modify", "modify", table, kwargs)

			text = "variable %s was modified, condition: %s  command: %s" % (kwargs['set_col'], condition, query)
			return getAlert(text, "good")

		else:
			return getAlert("No modifications made")
		


if __name__ == '__main__':
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':modify_port,})
	cherrypy.quickstart(modify())
