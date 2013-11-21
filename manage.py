"""
the dataserf - a digital laborer for behavioral scientists
Copyright (C) 2013 Christian Battista

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *
import common

@lg_authority.groups('auth')
class manage(object):

	@cherrypy.expose
	def index(self, **kwargs):

		cookie = cherrypy.request.cookie

		u = cherrypy.user.name

		#establish a table from the cookie
		table = common.getCookie("datamaster_table")

		#user has selected a table
		if kwargs.has_key('select'):
			table = kwargs['select']
			common.setCookie('datamaster_table', table)

		#user has removed a table
		if kwargs.has_key('remove'):

			p = mt.MongoAdmin("datamaster").db["user_tables"].posts
			t = kwargs['remove']

			#is this the currently active table?
			if table == t:
				common.removeCookie('datamaster_table', table)
				table = None

			mt.MongoAdmin("datamaster").db.drop_collection("%s_%s.posts" % (t, u))
			mt.MongoAdmin("datamaster").db.drop_collection("%s_%s_vars.posts" % (t, u))
			p.remove({'user':u, 'table':t})
			mt.MongoAdmin("datamaster").db["user_ul_files"].posts.remove({'user':u, 'table':t})
			common.activity_log('manage', 'remove table', t, kwargs)

		select_table, remove_table = self.table_choice(table, kwargs)

		#user has selected some variable
		if kwargs.has_key('choose'):
			if kwargs['choose'] == 'vars':
				datatable = "%s_%s" % (table, cherrypy.user.name)
				tableName = "%s_%s_vars" % (table, cherrypy.user.name)
				posts = mt.MongoAdmin("datamaster").db[tableName].posts
				for k in kwargs.keys():
					posts.remove({'name':k})
					posts.update({'name':k}, {'$set':{'var_type':kwargs[k]}}, upsert=True)
				common.activity_log("manage", "choose", table, kwargs)
	
		#if there's an active table
		if table:
			choose_vars = self.chooseVars(table)
			review_vars = common.variableTable("%s_%s" % (table, u))
			preview = common.preview("%s_%s" % (table, u), kwargs, manage_url)

		else:
			choose_vars = no_table
			review_vars = no_table
			preview = no_table							
			
	
		items = [['select table', select_table], ['choose variables', choose_vars], ['review variables', review_vars], ['remove table', remove_table], ['preview', preview]]

		accordion = getAccordion(items, contentID='manage-small')

		output = getPage(accordion, "manage", "manage")

		return output

	def table_choice(self, table, kwargs):
		"""choose table interface
		"""

		u = cherrypy.user.name
		posts = mt.MongoAdmin("datamaster").db["tables"].posts
		p = mt.MongoAdmin("datamaster").db["user_tables"].posts

		radios = []
		count = 0
		check = 0

		for row in p.find({'user':u}):
			count += 1
			if table == row['table']:
				check = count

			radios.append(row['table'])

		form = getRadios(radios, 'select', check)

		select_table = getForm(form, manage_url, legend = 'Select the table that you want to work with')

		form = getRadios(radios, 'remove')

		remove_table = getForm(form, manage_url, legend = 'Remove the selected table')

		return select_table, remove_table

	def chooseVars(self, table):
		"""Choose variables interface
		"""
		
		tableName = "%s_%s" % (table, cherrypy.user.name)

		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		var_posts = mt.MongoAdmin("datamaster").db["%s_vars" % tableName].posts
 
		try:
			headers = mt.GetKeys(posts)
		except:
			headers = []

		output = "<p>Which variables are you most interested in?  Use the radio buttons to indicate which variables are independent (IV) or dependent (DV).  You should also indicate which variables are the trial and subject info. </p>"""

		output += "<p>table: <em>%s</em><p>" % table

		table_data = []

		for h in headers:
			row = [h]

			for value in common.TVs + ['none']:
				inp = "<label class='radio'><input type = 'radio' name = '%s' value = '%s'/>%s</label>" % (h, value, value)
				var = var_posts.find_one({'name':h})
				#if this is a particular type of variable
				if var:
					var_type = var['var_type']
					if var_type == value:
						inp = "<label class='radio'><input type = 'radio' name = '%s' value = '%s' checked='checked'/>%s</label>" % (h, value, value)
				#otherwise it's none
				else:
					if value == 'none':
						inp = "<label class='radio'><input type = 'radio' name = '%s' value = '%s' checked='checked'/>%s</label>" % (h, value, value)
				row.append(inp)
			table_data.append(row)
		
		table_data = getTable(table_data)

		form = getForm(table_data, manage_url, hidden=['choose', 'vars'])

		output += form

		return output
		

if __name__ == '__main__':
#Turn on lg_authority for our website
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':manage_port,})
	cherrypy.quickstart(manage())

