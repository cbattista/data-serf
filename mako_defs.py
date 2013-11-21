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

no_table = "<p>You must select a table before performing this action.</p>"

def select_table(target, curTable = False):
	u = cherrypy.user.name
	posts = mt.MongoAdmin("datamaster").db["tables"].posts
	p = mt.MongoAdmin("datamaster").db["user_tables"].posts

	radios = []
	count = 0
	check = 0

	for row in p.find({'user':u}):
		count += 1
		if curTable:
			if curTable == row['table']:
				check = count

		radios.append(row['table'])

	form = getRadios(radios, 'select_table', check)

	select_table = getForm(form, target, legend = 'Select the table that you want to work with')

	return select_table

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
	</div>
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
	%if label:
		<label><em>${label}</em></label>
	%endif
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

<%def name = "mark_outliers(DVs)">
	<p>Mark as outlier where :
	${condition(DVs, "", "")}
	</p>
	<hr>
	<p>Or perform recursive outlier detection on 
	${options(DVs, "", "outlier-recurse-field", "")}
	using a Max Std Dev of <input type='number' step='0.1' name = 'outlier-maxSD' min='3.0'/>
	</p>
	Note : Recursive outlier detection will not consider values you have already marked as outliers.  Please note also this is a very CPU intensive function, so try not to overdo it.  Lastly, it is not currently advisable to use a maximum SD lower than 3.0, as this may cause the server to go a little bonkers (due to too much recursion).</p>
	<hr>

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

<%def name="support_content(domain)">
	<br/>
	<h2>You can support the dataserf by doing any or all of the following:</h2>
	<br/>
	<br/>
	<p><em>1. Tell your friends and colleagues.</em>  I can't market this site on my own.  If you find this site to be an invaluable tool, then let others know about it!  At this point I'm not too worried about overloading the site with users (indeed, my eventual plan is to crowdsource this baby into a self-sustaining site, where users basically pay for the CPU/server time they use, and that's it).</p>	
	<p><em>2. Find bugs.</em> I can't test every feature of this site on my own, so I rely on my users to submit bug reports.  Right now you can do this by just <a href="mailto:battista.christian@gmail.com?Subject=dataserf%20Bug%20Report" target="_top">emailing me</a>, but before you do, please check out the list of known bugs/issues that I already have, <a href='https://github.com/cbattista/dataserf/issues?state=open'>here</a>.</p>
	<p><em>3.  Fund the development of new features.</em>  Is there a feature you'd like to see?  Let me know!  Even if it's specific to your research, let me know - I have been writing custom code for the psych/neuro crowd for 10 years now, and I've gotten pretty good at it.  So <a href="mailto:battista.christian@gmail.com?Subject=dataserf%20Feature%20Request" target="_top">
contact me</a> about any potential features, and I can send you a quote - it might be cheaper than you think.  <em>Note:</em>  this also applies to fixing existing bugs.</p>
	<p><em>4.  Just donate.</em>  If you're impressed with the site, and want to see it grow and prosper, then consider just making a donation.  If you run a lab, then consider how much time you will free up for your grads and RAs to do more important things, like writing and data collection.  <a href="mailto:battista.christian@gmail.com?Subject=dataserf%20Donation" target="_top">Contact me </a> for more details about this (at this point, I want to establish a relationship with potential funders before accepting any money).  Current sponsors include : the <a href='http://www.numericalcognition.org'>Numerical Cognition Lab</a>.</p>

<hr>

<p>Not sure how much to give?  Here are some guidlines:</p>

<p><em>If you are an RA or a grad student...</em></p>

<p><b>$150 (or more)</b> a year can be helpful.  This would entitle you to tech support, and unlimited use of the site (certain CPU-intensive features, like recursive outlier detection, may sometimes need to be restricted to subscribers).  If you get an allowance for software/technology from your department, this can be a good way of spending it.  Alternatively, you can talk to your boss about getting a subscription for you or your lab.  On that note...</p>

<p><em>If you run a lab...</em></p>

<p><b>$500 (or more)</b> a year is suitable for a lab of up to 10 users.  This entitles each account assigned to your lab unlimited use of the site, as well as tech support.  At this level of funding, simple features/bug fixes may be requested - these include things like psychophysical funtions or custom files outputs (provided they are not too complex).</p>

<p><b>$1000 (or more)</b> a year is suitable for labs of up to 25 users, and includes all of the perks of a $500/yr subscription for all users associated with the lab.  Donations of this size also allow for more complex features to be developped, and bigger bugs/issues to be resolved.  Furthermore, generous donations like these provide me with the means to improve the codebase that runs the dataserf - making changes that non-programmers wouldn't necessarily notice, but that make the site run more efficiently.  <b>Even if you don't run a large lab, donations of this size go a long way towards improving the dataserf, for the benefit of all its users.</b></p>

</%def>

<%def name='learn_content(domain)'>
	<p>Greetings Lords and Ladies, my name is Christian and I am the guy who made the dataserf.  The dataserf is in its early stages, but I do believe though that it works well enough to perform some basic labours, including data modification and aggregation, for you.</p>
	<p>When you analyze your data, you usually have it organized in a spreadsheet that you put into SPSS or R (or some analysis program you like).  But before that happens, you need to organize all your individual subject files, average all the values, maybe changing the labels of some of your conditions or adjusting variables like reaction time.  This usually manifests itself as a whole pile of repetitive tasks that you don't want to do.</p>
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
	<p>Here's an important step.  When you upload your first set of files into a table, the dataserf will attempt to guess what the important variables are.  It will try to identify the subject, trial, and run/session variable based on the contents of your file.  It will also try to guess what the DVs are called, by looking for the terms 'ACC' and 'RT'.  But, it won't necessarily guess perfectly, and it won't be able to tell what your IVs are called.  So, you use the manage page to identify the IVs, DVs, and correct any mistakes it made trying to guess your subject, trial, and run/session variables.  Once you've selected them, you can review them to make sure you picked all the ones you're interested in (and you can always go back later and select some more).</p>

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
	<p>There is also some outlier detection functionality built in.  There are two things you can do - mark certain trials as outliers based on a static value, or use recursive outlier detection based on an SD threshold.  Right now recursive outlier detection operates on the entire table, but if I get the time I'd like to make it work on a subject-by-subject basis (check out the 'support' link at the top of the page to see how you can help make this happen faster.
	</p>

	</div>

	<div class="thumbnail" id="download-small">
	<h2>download</h2>
	<p>Here's the really magical part.  On this page, you can aggregate your data (for use in R or SPSS), download it either as a single file or one file per subject, and also download some PRTs (which is a file format needed for BrainVoyager).</p>
	<p>To aggregate just check off the variables you want to see in your file and you're off to the races.  Right now the file you'll get is one suitable for SPSS (where each participant's data is on a separate row).  They take a few seconds to make, but any files you create can be downloaded later on.</p>
	<p>Also, you have the option of including only certain values from your table.  You can specify this like you did in the 'Modify' section.</p>
	<p>To make PRT files, first indicate the Experiment Onset Delay - for instance if there is any lag between when the scanner started and when your stimulus display program started showing the stimuli.  If there's no lag, just leave it at zero</p>
	<p>Then indicate which variable contains the stimulus onset, and the offset (e.g., how long the stimulus lasted).  Then add a condition to group the onsets by.</p>
	<p>If you want to check the accuracy (and thus include an 'Error' column), indicate which variable contains the accuracy and reaction time.  The reason dataserf needs to know the reaction time is so that it in the event there are no errors, it will use the trial with the longest RT (BV does not like it when you don't have values in each condition).</p>
	<br/>
	</div>
	<p>And that's about it.  Click on the links below to get started (hint:  if this is your first time on the site, start in the upload section).</p>
	<p>If you need help with anything, please feel free to <a href="mailto:battista.christian@gmail.com?Subject=dataserf%20help%20request" target="_top"> contact me</a>.  The same goes for feature requests - I am always up for a little freelance work, and like it when I get a chance to improve the dataserf.  Check out the 'support' link at the top of the page for more info on this.</p>
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

def getSupportContent():
	output = template.get_def("support_content").render(lc=learn_url, domain=domain)
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
