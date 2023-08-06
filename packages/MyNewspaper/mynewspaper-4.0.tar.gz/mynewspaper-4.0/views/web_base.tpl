<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Cache-Control" content="no-cache"/>
  <title>MyNewspaper</title>
  <link rel="shortcut icon" href="/images/favicon.ico"/>
  <link type="text/css" rel="stylesheet" href="/static/default_web.css"/>
  <script type="text/javascript" charset="utf-8" src="/static/jquery.js"></script>
  <script type="text/javascript" charset="utf-8" src="/static/jqueryui.js"></script>
  <script type="text/javascript" charset="utf-8" src="/static/web_code.js"></script>
  <script type="text/javascript">
    $(document).ready(function() { mn_load("{{wis}}"); });
  </script>
</head>

<body>

  <div id="mn_title">
    <img src="/images/sidebar_off.png" id="img_sb" alt="Toggle sidebar"/>
    <a href="https://inigo.katxi.org/devel/mynewspaper" target="_blank">M y &nbsp; N e w s p a p e r </a>
    <span id="mn_copyright">&copy; 2005-14, I&ntilde;igo Serna</span>
    <img src="/images/refresh.png" id="img_refresh" alt="Refresh"/>
  </div>

  <div id="page">
    <div id="sidebar"></div>
    <div id="contents"></div>
  </div>

  <div id="overlay"></div>
  <div id="dialog"></div>
  <div id="dlg_loading"></div>
  <div id="dlg_help" tabindex="0"></div>
</body>
</html>
