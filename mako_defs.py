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

from mako.template import Template
import cherrypy
from config import *
import mt

def getPage(data, title="", contentID="", static=False):
	page_tpl = Template(filename="page.tpl")
	
	user = None

	if not static:
		if cherrypy.user:
			user = cherrypy.user.name

	output = page_tpl.render(data=data, title=title, user=user, main_url=main_url, urls=urls, domain=domain, contentID=contentID)
	
	return output

def getLogin():
	page_tpl = Template(filename='login.tpl')

	output = page_tpl.render(domain=domain, main_url=main_url, urls=urls)

	return output

no_table = "<p>You must select a table before performing this action.  <a href='%s'>Click here to select a table</a>.</p>" % manage_url

def getSuccess(data):
	output = "<div class='alert alert-success'>%s</div>" % data
	return output

def prettyList(l):
	output = ""
	for item in l:
		output += item + ', '

	output.rstrip(', ')

	return output

template = Template("""
<%def name = "table(data, title)">
	<div class="table">
	<table>
	%if title:
		<h3>${title}</h3>
	%endif
	<table>
	%for row in data:
		<tr>
		%for r in row:
			<td>${r}</td>
		%endfor
		</tr>
	%endfor
	</table>
	</%def>

<%def name = "form(data, form_action, btntext, legend, hidden)">
	%if form_action:
		<form action="${form_action}">
	%else:
		<form>
	%endif
	<fieldset>
	%if legend:
		<legend>${legend}</legend>
	%endif
	%if hidden:	
		<input type="hidden" name="${hidden[0]}" value="${hidden[1]}">
	%endif
	${data}
	<br/>
	%if btntext:
		<button type="submit" class="btn">${btntext}</button>
	%else:
		<button type="submit" class="btn">Submit</button>
	%endif
	</fieldset>
	</form>
</%def>

<%def name = "radiobuttons(buttons, name, checkbox)">
	%for button in buttons:
	<label class="radio">
		%if (buttons.index(button) + 1) == checkbox:
			<input type="radio" name="${name}" value="${button}" checked='checked'>
		%else:
			<input type="radio" name="${name}" value="${button}">
		%endif
		${button}
	</label>
	%endfor
</%def>


<%def name = "setter(var_options, label, number)">
	<label><em>${label}</em></label>

	<select name='set_col${number}'>
	<option/>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='set_op${number}'>
		<option></option>
		<option>=</option>
		<option>+=</option>
		<option>-=</option>
	</select>
	<select name='set_val${number}'>
	<option/>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	or 
	<input type='text' name = 'set_text${number}' />

</%def>

<%def name="options(options, label, ID, active)">
	%if ID:
		<select name='op-${ID}'>
	%else:
		<select name='op'>
	%endif
	%for o in options:
		%if active == o:
			<option selected='selected'>${o}</option>
		%else:
			<option>${o}</option>
		%endif
	%endfor
	</select>
</%def>	

<%def name = "condition(var_options, label, number)">
	<label><em>${label}</em></label>

	<select name='if_var${number}'>
	<option></option>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='if${number}'>
		<option/>
		<option>==</option>
		<option>!=</option>
		<option>>=</option>
		<option>></option>
		<option><=</option>
		<option><</option>
	</select>
	<input type='text' name='if_text${number}' />
</%def>

<%def name = "create_column(var_options)">
	<legend>create a new variable</legend>
	<label><em>Name</em> (required)</label>
	<input type='text' name='new_var'>
	<select name='new_var_type'>
		<option>IV</option>
		<option>DV</option>
		<option>subject</option>
		<option>trial</option>
	</select>
	<label><em>From</em> (optional)</label>
	<select name='orig_var'>
	<option></option>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='op'>
		<option/>
		<option>+=</option>
		<option>-=</option>
	</select>
	<input type='text' name='op_text' />
</%def>

<%def name = "merge_column(var_options)">
	<legend>merge two variables into a new variable</legend>
	<label><em>Name</em> (required)</label>
	<input type='text' name='merge_var'> 
	<select name='merge_var_type'>
		<option>IV</option>
		<option>DV</option>
		<option>subject</option>
		<option>trial</option>
	</select>
	<label><em>Source variables</em> (required)</label>
	<select name='var_left'>
	<option></option>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='op'>
		<option/>
		<option>+</option>
		<option>-</option>
		<option>*</option>
		<option>/</option>
		<option>join text</option>
	</select>

	<select name='var_right'>
	<option></option>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
</%def>

<%def name = "accordion(items, startIndex, contentID)">
	<div class="accordion">
		%for item in items:
		<div class="accordion-group">
			<div class="accordion-heading" id="${contentID}">
				<a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion2" href="#collapse${items.index(item) + startIndex}"><h2>${item[0]}</h2></a>
			</div>
			<div id="collapse${items.index(item) + startIndex}" class="accordion-body collapse">
				<div class="accordion-inner">
					${item[1]} 
				</div>
			</div>
		</div>
		%endfor
	</div>
</%def>

<%def name="index_content(lc, domain)">
	   <img src='${domain}/serf.png' align='right' />
		<h1>dataserf</h1>
       <p>The dataserf provides digital labor for behavioral scientists.  Upload your raw data files from programs like E-Prime and format them so they're ready for use in a stats program like SPSS or R.</p>
        <p><a class="btn btn-inverse btn-large" href="${lc}">Learn more &raquo;</a></p>

</%def>

<%def name='learn_content(domain)'>
	<p>Greetings Lords and Ladies, my name is Christian and I am the guy who made the dataserf.  The dataserf is in its early stages, but I do believe though that it works well enough to perform some basic labours, including data modification and aggregration, for you.</p>
	<p>When you analyze your data, you usually have it organized in a spreadsheet that you put into SPSS or R or something.  But before that happens, you need to organize all your individual subject files, average all the values, maybe changing the labels of some of your conditions or adjusting variables like reaction time.  This usually manifests itself as a whole pile of repetitive tasks that you don't want to do.</p>
	<p>The dataserf was built to do these tasks for you.  It will put your data into a storage unit called a <em>table</em>.  Each table is a place to hold data from all your subjects for a given experiment.</p>
	<p>Once the dataserf has your data in a table, it can modify the <em>variables</em>.  A variable is a value from a column in your spreadsheet.  So this might be your reaction time data, accuracy, or your experimental conditions.</p>
	<p>Using a table, the dataserf can also average your data into a summary spreadsheet for you to download.</p>
	<br/>
	<p>Now that we've covered the basics, we are ready to learn the 4 labors the dataserf knows how to perform...</p>
	<br/>
	<h1>labors of the dataserf</h1>

	<div class="thumbnail" id="upload-small">
	<h2>upload</h2>
	<p>If you've just started using the dataserf, the first thing you need to do is create a table for your data to be stored in.  Then you select the files you want to upload.  At this point, the dataserf can handle those weird .txt files that E-Prime spits out and also any .csv files that have titles for the columns.  Don't try to upload those .edat type files though, that won't work (use the weird .txt files instead).  The dataserf can also handle comma separated value files (e.g., .csv files).  The dataserf will assume that .csv files have a trial's worth of data on each row, and that the first row contains the column labels.</p>
	<p>Once you've selected your files, you can upload them (it may take a bit for them to upload, usually I have to wait about a minute for 40 files to get onto the server).</p>
	<p>When the files have uploaded, you can review them and make sure they all uploaded.  Later on if you decide you want to remove some of them from the table, you can go to the review section to pull some out.</p>
	</div>	

	<div class="thumbnail" id = "manage-small">
	<h2>manage</h2>
	<p>Here's an important step.  This is where you tell the dataserf what variables you're interested in.  You should indicate what your independent variables and dependent variables are, and also what variable name you're using to indicate your subject and trial variables.  Once you've selected these, you can review them to make sure you picked all the ones you're interested in (and you can always go back later and select some more).</p>
	</div>

	<div class="thumbnail" id="modify-small">
	<h2>modify</h2>
	<p>This one's optional - sometimes you need to change a variable or add a new one - here's where you do that.  You can make a new variable, either from scratch or based off an existing one.</p>
	<p>You can also make a new variable by merging two existing variables.  If they're numbers you can add, subtract, multiply or divide them.  If they're text variables, then you can join them together using 'join text'.</p>
	<p>The last thing you can do is transform a variable, either applying the change to all the values or only to some of them.  Here's an example : a common thing psych types need to do is apply an RT penalty when a participant gets a question wrong.  So let's say you have the variables RT (reaction time, in seconds) and ACC (accuracy, where 1 is correct and 0 is incorrect).  And let's say you wanted to add 200 milliseconds to all the RTs where the participant made an incorrect response.  Here's what you would do:</p>
	<p>If ACC == 0</p>
	<p>Set RT += .2</p>
	<p>Another thing you might want to do is set the accuracy to zero if the reaction time is above a certain threshold, say 2.5 seconds.  In that case, you would do:</p>
	<p>If RT >= 2.5</p>
	<p>Set ACC = 0</p>
	<p>Pretty simple, huh?</p>
	</div>

	<div class="thumbnail" id="download-small">
	<h2>download</h2>
	<p>Here's the really magical part.  Just check off the variables you want to see in your file and you're off to the races.  Right now the file you'll get is one suitable for SPSS (where each participant's data is on a separate row).  They take a bit to make, but any files you create can be downloaded later on.</p>
	<p>Also, you have the option of including only certain values from your table.  You can specify this like you did in the 'Modify' section.</p>
	<br/>
	</div>
	<p>And that's about it.  Click on the links below to get started (hint:  if this is your first time on the site, start in the upload section).</p>
</%def>

""")


def getRadios(buttons, name="", check=0):
	output = template.get_def("radiobuttons").render(buttons=buttons, name=name, checkbox=check)
	return output

def getCheckbox(myList, br=False):
	output = ""
	for l in myList:
		output += "<label class='checkbox'><input type='checkbox' name='%s'/>%s</label>" % (l, l)
		if br:
			output += "<br/>"
	return output


def getCondition(var_options, label="", ID=""):
	output = template.get_def("condition").render(var_options=var_options, label=label, number=ID)
	return output

def parseCondition(kwargs):
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

	return condition

def getOptions(options, label="", ID="", active=""):
	output = template.get_def("options").render(options=options, label=label, ID=ID, active=active)
	return output

def getSetter(var_options, label="", ID=""):
	output = template.get_def("setter").render(var_options=var_options, label=label, number=ID)
	return output

def getLearnContent():
	output = template.get_def("learn_content").render(domain=domain)
	return output

def getIndexContent():
	output = template.get_def("index_content").render(lc=learn_url, domain=domain)
	return output

def getAccordion(items, startIndex=0, contentID=""):
	output = template.get_def("accordion").render(items=items, startIndex=startIndex, contentID=contentID)
	return output

def getAlert(text, status='bad'):
	if status == 'bad':
		alert = 'alert alert-error'
	elif status == 'good':
		alert = 'alert alert-success'
	else:
		alert = 'alert'

	return '<div class="%s">%s</div>' % (alert, text)

def getTable(data, title=""):
	output = template.get_def("table").render(data=data, title=title)
	return output

def getForm(data, form_action="", btn_text = "", legend = "", hidden=[]):
	output = template.get_def("form").render(data=data, form_action=form_action, btntext=btn_text, legend=legend, hidden=hidden)
	return output
