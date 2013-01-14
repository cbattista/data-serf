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
from mako_defs import *
from config import *
import cherrypy

def make_pages():
	d = {}
	d['50x'] = """<h3>attempting to perform a labour</h3><h2>that he could not perform</h2>"""
	 
	d['403'] = """<h3>attempting to walk a path</h3><h2>which was forbidden to him</h2>"""
	d['404'] = """<h3>attempting to find a place</h3><h2>which did not exist</h2>"""

	for page in ['50x', '403', '404']:

		f = open('%s.html' % page, 'w')

		img = """
			<img src='%s/fallen_serf.png' align='right'/>
			<h1>oh my</h1>
			<h3>he has fallen</h3>
			%s
		""" % (domain, d[page])

		pageContent = getPage(img, '', static=True)

		f.write(pageContent)

	f.close()

def make_login():
	f = open("login.html", 'w')
	content = getLogin() 
	f.write(content)
	f.close()

make_login()
