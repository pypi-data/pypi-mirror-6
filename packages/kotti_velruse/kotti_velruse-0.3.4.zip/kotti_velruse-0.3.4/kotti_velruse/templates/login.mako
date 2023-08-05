<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<title>${project} :: Login</title>
	<!-- Simple OpenID Selector -->
	<link type="text/css" rel="stylesheet" href="css/openid.css" />
	<link type="text/css" rel="stylesheet" href="/fanstatic/bootstrap/css/bootstrap.css" />
	<script type="text/javascript" src="js/jquery-1.2.6.min.js"></script>
	<script type="text/javascript" src="js/openid-jquery.js"></script>
	<script type="text/javascript" src="js/openid-en.js"></script>
	<script type="text/javascript">
		$(document).ready(function() {
			openid.init('openid_identifier');
			openid.setDemoMode(false); //Stops form submission for client javascript-only test purposes
		});
	</script>
	<!-- /Simple OpenID Selector -->
	<style type="text/css">
		/* Basic page formatting */
		body {
			font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
		}
	</style>
</head>

<body>
    <div class="container">
	<h2>Login to ${project}</h2>
	<!-- Simple OpenID Selector -->
	<form action="${login_url}" method="post" id="openid_form">
		<input type="hidden" id="action"    name="action" value="verify" />
		<input type="hidden" id="method"    name="method" value="unknown" />
                <input type="hidden" id="came_from" name="came_from" value="${came_from}" />
		<fieldset>
			<legend>Sign-in</legend>
			<div id="openid_choice">
				<p>Please click your account provider</p>
				<div id="openid_btns"></div>
			</div>
			<div id="openid_input_area">
				<p id="openid_label">Enter your OpenID to any provider</p>
				<input type="text"   id="openid_username" value="" />
				<input type="submit" id="openid_submit"   value="Sign-in"
						     style="margin-left:10px; margin-bottom: 10px;" class="btn btn-success" />
			</div>
		</fieldset>
	</form>
	<p><small>OpenID allows you to log-on to many different websites using a single identity.<br/>
           Find out <a href="http://openid.net/what/">more about OpenID</a> and
           <a href="http://openid.net/get/">how to get an OpenID enabled account</a>.</small></p>
    </div>
</body>
</html>
