from mako.template import Template
import cherrypy
from config import *

def getPage(data, title="", contentID=""):
	page_tpl = Template(filename="page.tpl")
	if cherrypy.user:
		name = cherrypy.user.name
		output = page_tpl.render(data=data, title=title, user=name, main_url=main_url, urls=urls, domain=domain, contentID=contentID)
	else:
		output = page_tpl.render(data=data, title=title, user=None, main_url=main_url, urls=urls, domain=domain, contentID=contentID)
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
	</div>
	</%def>

<%def name = "form(data, form_action, btntext)">
	<fieldset>
	%if form_action:
		<form action="${form_action}">
	%else:
		<form>
	%endif
	${data}
	<br/>
	%if btntext:
		<button type="submit" class="btn">${btntext}</button>
	%else:
		<button type="submit" class="btn">Submit</button>
	%endif
	</form>
	</fieldset>
	</%def>

<%def name = "condition(var_options, label)">
	<em>${label}</em>
	<select name='if_var'>
	<option></option>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='if'>
		<option/>
		<option>==</option>
		<option>!=</option>
		<option>>=</option>
		<option>></option>
		<option><=</option>
		<option><</option>
	</select>
	<input type='text' name='if_text' />
</%def>

<%def name = "modify(var_options)">
	<h2>transform an existing variable</h2>
	<label><em>If</em> (optional)
	<select name='if_var'>
	<option></option>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='if'>
		<option/>
		<option>==</option>
		<option>>=</option>
		<option>></option>
		<option><=</option>
		<option><</option>
	</select>
	<input type='text' name='if_text' />
	</label>
	<label><em>Set</em> (required)
	<select name='set_col'>
	<option/>
	%for vo in var_options:
		<option>${vo}</option>
	%endfor
	</select>
	<select name='set_op'>
		<option/>
		<option>=</option>
		<option>+=</option>
		<option>-=</option>
	</select>
	<input type='text' name = 'set_text' /></label>
</%def>

<%def name = "create_column(var_options)">
	<h2>create a new variable</h2>
	<label><em>Name</em> (required)
	<input type='text' name='new_var'>
	<select name='new_var_type'>
		<option>IV</option>
		<option>DV</option>
		<option>subject</option>
		<option>trial</option>
	</select>
	</label>
	<label><em>From</em> (optional)
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
	</label>
</%def>

<%def name = "merge_column(var_options)">
	<h2>merge two variables into a new variable</h2>
	<label><em>Name</em> (required)
	<input type='text' name='merge_var'> 
	<select name='merge_var_type'>
		<option>IV</option>
		<option>DV</option>
		<option>subject</option>
		<option>trial</option>
	</select>
	</label>
	<label><em>Source variables</em> (required)
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
	</label>
</%def>

<%def name = "accordion(items, startIndex)">
	<div class="accordion">
		%for item in items:
		<div class="accordion-group">
			<div class="accordion-heading">
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

<%def name="index_content(lc)">
       <p>The dataserf provides digital labor for behavioral scientists.  Upload your raw data files from programs like E-Prime and format them so they're ready for use in a stats program like SPSS or R.</p>
        <p><a class="btn btn-primary btn-large" href="${lc}">Learn more &raquo;</a></p>

</%def>

<%def name='learn_content()'>
	<p>Greetings Lords and Ladies, my name is Christian and I am the guy who made the dataserf.  The dataserf is in its early stages, but I do believe though that it works well enough to perform some basic labours, including data modification and aggregration, for you.</p>
	<p>When you analyze your data, you usually have it organized in a spreadsheet that you put into SPSS or R or something.  But before that happens, you need to organize all your individual subject files, average all the values, maybe changing the labels of some of your conditions or adjusting variables like reaction time.  This usually manifests itself as a whole pile of repetitive tasks that you don't want to do.</p>
	<p>The dataserf was built to do these tasks for you.  It will put your data into a storage unit called a <em>table</em>.  Each table is a place to hold data from all your subjects for a given experiment.</p>
	<p>Once the dataserf has your data in a table, it can modify the <em>variables</em>.  A variable is a value from a column in your spreadsheet.  So this might be your reaction time data, accuracy, or your experimental conditions.</p>
	<p>Using a table, the dataserf can also average your data into a summary spreadsheet for you to download.</p>
	<br/>
	<p>Now that we've covered the basics, we are ready to learn the 4 labors the dataserf knows how to perform...</p>
	<br/>
	<h1>labors of the dataserf</h1>

	<div id="upload">
	<h2>upload</h2>
	<p>If you've just started using the dataserf, the first thing you need to do is create a table for your data to be stored in.  Then you select the files you want to upload.  At this point, the dataserf can handle those weird .txt files that E-Prime spits out and also any .csv files that have titles for the columns.  Don't try to upload those .edat type files though, that won't work (use the weird .txt files instead).  The dataserf can also handle comma separated.  The dataserf will assume that files like this have a trial's worth of data on each row, and that the first row contains the column labels.</p>
	<p>Once you've selected your files, you can upload them (it may take a bit for them to upload, usually I have to wait about a minute for 40 files to get onto the server).</p>
	<p>When the files have uploaded, you can review them and make sure they all uploaded.  Later on if you decide you want to remove some of them from the table, you can go to the review section to pull some out.</p>
	</div>	

	<div id = "manage">
	<h2>manage</h2>
	<p>Here's an important step.  This is where you tell the dataserf what variables you're interested in.  You should indicate what your independent variables and dependent variables are, and also what variable name you're using to indicate your subject and trial variables.  Once you've selected these, you can review them to make sure you picked all the ones you're interested in (and you can always go back later and select some more).</p>
	</div>

	<div id="modify">
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

	<div id="download">
	<h2>download</h2>
	<p>Here's the really magical part.  Just check off the variables you want to see in your file and you're off to the races.  Right now the file you'll get is one suitable for SPSS (where each participant's data is on a separate row).  They take a bit to make, but any files you create can be downloaded later on.</p>
	<p>Also, you have the option of including only certain values from your table.  You can specify this like you did in the 'Modify' section.</p>
	<br/>
	</div>
	<p>And that's about it.  Click on the links below to get started.</p>
</%def>

""")

def getCheckbox(myList, br=False):
	output = ""
	for l in myList:
		output += "<label class='checkbox'><input type='checkbox' name='%s'/>%s</label>" % (l, l)
		if br:
			output += "<br/>"
	return output

def getCondition(var_options, label=""):
	output = template.get_def("condition").render(var_options=var_options, label=label)
	return output

def getLearnContent():
	output = template.get_def("learn_content").render()
	return output

def getIndexContent():
	output = template.get_def("index_content").render(lc=learn_url)
	return output

def getAccordion(items, startIndex=0):
	output = template.get_def("accordion").render(items=items, startIndex=startIndex)
	return output

def getTable(data, title=""):
	output = template.get_def("table").render(data=data, title=title)
	return output

def getForm(data, form_action="", btn_text = ""):
	output = template.get_def("form").render(data=data, form_action=form_action, btntext=btn_text)
	return output
