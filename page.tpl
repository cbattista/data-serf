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


	<!-- Les Analytiques de Google -->
	<script>
	  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

	  ga('create', 'UA-48213005-1', 'christianbattista.com');
	  ga('send', 'pageview');

	</script>

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
	<link href='http://fonts.googleapis.com/css?family=Gentium+Book+Basic|Rye|UnifrakturCook:700' rel='stylesheet' type='text/css'>


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
          <a class="brand" href="${urls[0]}">dataserf</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li class="active"><a href="${urls[0]}">home</a></li>
              <li><a href="${urls[5]}">about</a></li>
			%if user:
			  <li><a href="${urls[0]}/auth">${user}</a></li>
			  <li><a href="${urls[0]}/auth/logout">logout</a></li>
			%endif
		<li><a href="${urls[6]}">support the dataserf</a></li>
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




	    <div class="row-fluid">

        <li class="span3">
	      <div class="thumbnail" id="upload-small">
          <h2>upload</h2>
           <p>Upload some files or review the ones you've already uploaded.</p>
          <a class="btn" href="${urls[1]}">Upload some files.&raquo;</a>
		  </div>
        </li>

        <li class="span3">
		  <div class="thumbnail" id="manage-small">
          <h2>manage</h2>
           <p>Identify the variables you are interested in.</p>
          <a class="btn" href="${urls[2]}">Manage your data &raquo;</a>
		  </div>
       </li>

        <li class="span3">
		  <div class="thumbnail" id="modify-small">
          <h2>modify</h2>
           <p>Edit your variables and create new ones.</p>
          <a class="btn" type="button" href="${urls[3]}">Modify your data &raquo;</a>
		  </div>
       </li>

        <li class="span3">
		  <div class="thumbnail" id="download-small">
          <h2>download</h2>
          <p>Aggregate your data and download it.</p>
          <a class="btn" href="${urls[4]}">Download some files &raquo;</a>
		  </div>
        </li>

   	  </ul>
      </div>

	  <hr>
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
