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

#client.py
import mt

def parseQuery(kwargs):
	q = {}

	qdict={}
	qdict['>='] = '$gte'
	qdict['>'] = '$gt'
	qdict['<='] = '$lte'
	qdict['<'] = '$lt'
	qdict['!='] = '$ne'

	value = mt.StringToType(kwargs['if_text'])
	key = kwargs['if_var']
	cond = kwargs['if']

	if value and key and cond:

		if cond == '==':
			q = {key : value}
		else:
			subcond = {qdict[cond] : value}
			q = {key : subcond}

	else:
		
		q = {}

	return q
