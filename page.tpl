<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>dataserf - yes m'lord</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

	<!-- Le jquery -->
    <script src="${domain}/assets/js/jquery.js"></script>

    <!-- Le styles -->
    <link href="${domain}/assets/css/bootstrap.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <link href="${domain}/assets/css/bootstrap-responsive.css" rel="stylesheet">
    <link href="${domain}/assets/css/dataserf.css" rel="stylesheet">

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Le fav and touch icons -->
    <link rel="shortcut icon" href="${domain}/shovel.ico">
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="${main_url}/assets/ico/apple-touch-icon-144-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="${main_url}/assets/ico/apple-touch-icon-114-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="${main_url}/assets/ico/apple-touch-icon-72-precomposed.png">
    <link rel="apple-touch-icon-precomposed" href="${domain}/assets/ico/apple-touch-icon-57-precomposed.png">
  </head>

  <body>

    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="#">dataserf</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li class="active"><a href="${domain}">Home</a></li>
              <li><a href="${urls[5]}">About</a></li>
			%if user:
			  <li><a href="#">Logged in as ${user}</a></li>
			  <li><a href="auth/logout">Logout</a></li>
			%endif
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">

      <!-- Main hero unit for a primary marketing message or call to action -->
	  %if contentID:
	      <div class="hero-unit" id = "${contentID}">
      %else :
	      <div class="hero-unit">
	  %endif
        <h1>${title}</h1>
		<div id="content">${data}</div>
      </div>

      <hr>


	    <div class="row-fluid">

        <li class="span3">
	      <div class=thumbnail" id="upload">
          <h2>upload</h2>
           <p>Upload some files or review the ones you've already uploaded.</p>
          <p><a class="btn" href="${urls[1]}">Upload some files.&raquo;</a></p>
		  </div>
        </li>

        <li class="span3">
		  <div class=thumbnail" id="manage">
          <h2>manage</h2>
           <p>Identify the variables you are interested in.</p>
          <p><a class="btn" href="${urls[2]}">Manage your data &raquo;</a></p>
		  </div>
       </li>

        <li class="span3">
		  <div class=thumbnail" id="modify">
          <h2>modify</h2>
           <p>Edit your variables and create new ones.</p>
          <p><a class="btn" href="${urls[3]}">Modify your data &raquo;</a></p>
		  </div>
       </li>

        <li class="span3">
		  <div class=thumbnail" id="download">
          <h2>download</h2>
          <p>Aggregate your data and download it.</p>
          <p><a class="btn" href="${urls[4]}">Download some files &raquo;</a></p>
		  </div>
        </li>

   	  </ul>
      </div>

      <footer>
        <p>&copy; 2012 Christian Battista's dataserf</p>
      </footer>

    </div> <!-- /container -->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="${domain}/assets/js/bootstrap-transition.js"></script>
    <script src="${domain}/assets/js/bootstrap-alert.js"></script>
    <script src="${domain}/assets/js/bootstrap-modal.js"></script>
    <script src="${domain}/assets/js/bootstrap-dropdown.js"></script>
    <script src="${domain}/assets/js/bootstrap-scrollspy.js"></script>
    <script src="${domain}/assets/js/bootstrap-tab.js"></script>
    <script src="${domain}/assets/js/bootstrap-tooltip.js"></script>
    <script src="${domain}/assets/js/bootstrap-popover.js"></script>
    <script src="${domain}/assets/js/bootstrap-button.js"></script>
    <script src="${domain}/assets/js/bootstrap-collapse.js"></script>
    <script src="${domain}/assets/js/bootstrap-carousel.js"></script>
    <script src="${domain}/assets/js/bootstrap-typeahead.js"></script>
  </body>
</html>
