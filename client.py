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

	if cond == '==':
		q = {key : value}
	else:
		subcond = {qdict[cond] : value}
		q = {key : subcond}

	return q
