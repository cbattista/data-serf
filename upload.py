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

import cherrypy
import lg_authority
from mako_defs import *
from config import *
import common

@lg_authority.groups('auth')
class upload(object):

	#Allow everyone to see the index page

	@cherrypy.expose
	def index(self, **kwargs):
		u = cherrypy.user.name
		posts = mt.MongoAdmin("datamaster").db["tables"].posts

		output = ""

		cookie = cherrypy.request.cookie
		if cookie.has_key('datamaster_table'):
			table = cookie["datamaster_table"].value
		else:
			table = None

		if kwargs.has_key('table'):
			#create a new table if necessary
			if kwargs['table'] == 'new':
				p = mt.MongoAdmin("datamaster").db["user_tables"].posts
				if not p.find_one({'user':cherrypy.user.name, 'table':kwargs['new_table']}):
					p.insert({'table': kwargs['new_table'], 'user':cherrypy.user.name})
				table = kwargs['new_table']
	
			select_files = self.select(kwargs)

		elif table:
			select_files = self.select({'table':table})
		else:
			select_files = no_table

		if kwargs.has_key('myFiles'):
			ul_msg = self.upload(kwargs['myFiles'])
			output += getSuccess("Files uploaded successfully.")
		else:
			ul_msg = "<p>You haven't uploaded any files this session.</p>"

		if kwargs.has_key('table_remove'):
			self.remove(kwargs)
			output += getSuccess("Files removed successfully.")

		upload_files = ""

		items = [['select a table', self.select_table(table)], ['select your files', select_files], ['review files', self.review()]]

		output += getAccordion(items, contentID = 'upload-small')

		return getPage(output, "upload", "upload")

	def select_table(self, table):
		"""Select table interface maker
		"""
		#table selector
		select_table = ""
		p = mt.MongoAdmin("datamaster").db["user_tables"].posts
		select_table += """
		<p>Enter the name of a new table</p>
		<input type='radio' name='table' value='new'>New table called <input type ='text' name='new_table'/></input><br/>
		<p>or select one from the list below</p>

		"""

		print "select_Table %s" % table

		for row in p.find({'user':cherrypy.user.name}):
			if row['table'] == table:
				select_table += "<label><input type='radio' name='table' value='%s' checked='checked'>%s</input></label><br/>" % (row['table'], row['table'])
			else:
				select_table += "<label><input type='radio' name='table' value='%s'>%s</input></label><br/>" % (row['table'], row['table'])

		select_table = getForm(select_table, upload_url)

		return select_table

	def remove(self, kwargs):
		table = kwargs['table_remove']
		posts = mt.MongoAdmin("datamaster").db["%s_%s" % (table, cherrypy.user.name)].posts
		ul_files = mt.MongoAdmin("datamaster").db["user_ul_files"].posts
		for k in kwargs.keys():
			if kwargs != 'table_remove':
				posts.remove({'source_file':k})
				ul_files.remove({'file_name':k})

				common.activity_log('upload', 'remove', table, {'filename': k})

	def select(self, kwargs):
		if kwargs['table'] == 'new':
			table = kwargs['new_table']
		else:
			table = kwargs['table']
		
		cherrypy.response.cookie['datamaster_table'] = table
		cherrypy.response.cookie['datamaster_table']['path'] = '/'

		output = ""

		output +=  """
			<p>
			<form method="post" enctype="multipart/form-data">
			<input type="file" name="myFiles" multiple="multiple"/><br />
			<input type="submit"/>
			</form>
			</p>
		"""

		return output

	def upload(self, myFiles):
		p = mt.MongoAdmin("datamaster").db["user_tables"].posts
		cookie = cherrypy.request.cookie
		tableName = cookie["datamaster_table"].value 
		uf = mt.MongoAdmin("datamaster").db["user_ul_files"].posts

		output = "<p>" 

		output += str(type(myFiles))

		if type(myFiles) != list:
			myFiles = [myFiles]

		for myFile in myFiles:
			lines = []

			while True:
				data = myFile.file.readlines(100)
				if not data:
				    break
				lines += data
			if len(lines) == 1:
				lines = lines[0].split('\r')

			d = {'source_file' : myFile.filename}

			r = mt.ReadTable(None, "datamaster", "%s_%s" % (tableName, cherrypy.user.name), data=lines, kind="eprime", addrow = d)

			output += "The contents of %s have been uploaded.<br/>" % myFile.filename
			uf.insert({'user':cherrypy.user.name, 'table':tableName, 'file_name' : myFile.filename})

		output += "</p>"
	
		common.activity_log('upload', 'upload', tableName)

		#take a look at what variables we might have
		VARs = common.inspect("%s_%s" % (tableName, cherrypy.user.name))

		print VARs
		#mark 'em
		common.markVariables("%s_%s" % (tableName, cherrypy.user.name), VARs)

		return output

	def review(self):
		ut = mt.MongoAdmin("datamaster").db["user_tables"].posts
		uf = mt.MongoAdmin("datamaster").db["user_ul_files"].posts		

		items = []
		for row in ut.find({'user' : cherrypy.user.name}):
			t = row['table']

			l = []
			for other_row in uf.find({'user' : cherrypy.user.name, 'table': t}):
				l.append(other_row['file_name'])

			form = "<p>Select any files you wish to remove from your database</p>"
			inp = "<input type = 'text' name = 'table_remove' value='%s' style = 'visibility:hidden'></input>" % t
			form += getForm(inp + getCheckbox(l), upload_url, btn_text="Remove")			

			items.append([t, form])

		output = getAccordion(items, 3)

		return output

if __name__ == '__main__':

	cherrypy.config.update({'server.socket_port':upload_port})
	cherrypy.config.update(cherry_settings)
	cherrypy.quickstart(upload())

