#common.py

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

import mt
import cherrypy

def getVariables(table, sids=False):
	var_table = "%s_vars" % table

	dm = mt.MongoAdmin("datamaster")
	VARs = mt.MongoAdmin("datamaster").db[var_table].posts

	sid = VARs.find_one({'var_type': 'subject'})['name']
	trial = VARs.find_one({'var_type': 'trial'})['name']
	IVs = VARs.find({'var_type': 'IV'}).distinct('name')
	DVs = VARs.find({'var_type': 'DV'}).distinct('name')

	output = [sid, trial, IVs, DVs]

	if sids:
		sids = dm.db[table].posts.find().distinct(sid)
		output.append(sids)

	return output
