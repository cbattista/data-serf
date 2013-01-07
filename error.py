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

f = open('50x.html', 'w')

img = """
		<img src='%s/fallen_serf.png' align='right'/>
		<h1>oh my</h1>
		<h3>he has fallen</h3>
		<h3>attempting to perform a labour</h3>
		<h2>whose secrets were unknown to him</h2>
	  """ % domain

pageContent = getPage(img, '', static=True)

f.write(pageContent)

f.close()
