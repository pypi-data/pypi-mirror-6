<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
  <meta http-equiv="Pragma" content="no-cache"/>
  <meta http-equiv="Cache-Control" content="no-cache"/>
  <title>MyNewspaper: Setup wizard</title>
  <link rel="shortcut icon" href="/images/favicon.ico"/>
  <link type="text/css" rel="stylesheet" href="/static/default_web.css"/>
  <script type="text/javascript" charset="utf-8" src="/static/jquery.js"></script>
  <script type="text/javascript">
    function toggle($this) {
        $("input:file").hide();
        if ($this.val() == "opml")
            $("input:file:eq(0)").show();
        else if ($this.val() == "googlereader")
            $("input:file:eq(1)").show();
    }

    function check_file() {
        var val = $("input[name=init_feeds]:checked").val();
        if (val=="opml" && $("input:file:eq(0)").val()=="" || val=="googlereader" && $("input:file:eq(1)").val()=="") {
            alert('Please, select a file');
            return false;
        } else if (val=="migrate") {
            alert('Please, consult the documentation');
            window.open("/docs")
            return false;
        }
        $("#setup").hide();
        $("#page").append("<br/><br/><br/><div class='loading'><div>Loading...</div><br/><img src='/images/loading.gif' /></div>");
    }
  </script>
</head>
<body><center>

  <div id="mn_title">
    M y &nbsp; N e w s p a p e r
    <span id="mn_copyright">(C) 2005-14, I&ntilde;igo Serna</span>
  </div>
  <div id="mn_title">
    <a href="https://inigo.katxi.org/devel/mynewspaper" target="_blank">M y &nbsp; N e w s p a p e r </a>
    <span id="mn_copyright">&copy; 2005-14, I&ntilde;igo Serna</span>
  </div>
  <div id="page">
    <div id="setup">
      <div class="header">Setup wizard</div>
      <div class="paragraph">
        <p>Welcome to <b>MyNewspaper</b>!</p>
        <p>This is the initial wizard to configure the basics of the application.<br/>
          Please select how do you want to initialize <b>MyNewspaper</b>.<br/>
          <form name="wizard" action="/do_wizard" method="post" enctype="multipart/form-data">
            <span class="title">Initialize database with...</span>
            <br/>
            <input type="radio" name="init_feeds" value="blank" onclick="toggle($(this));" checked />&nbsp;No feeds<br/>
            <input type="radio" name="init_feeds" value="opml" onclick="toggle($(this));"/>&nbsp;Import feeds from an OPML file&nbsp;
            <input type="file" name="opmlfile" style="display: none;"/><br/>
            <input type="radio" name="init_feeds" value="googlereader" onclick="toggle($(this));"/>&nbsp;Import feeds from Google Reader takeout file&nbsp;
            <input type="file" name="googlereaderfile" style="display: none;"/><br/>
            <input type="radio" name="init_feeds" value="migrate" onclick="toggle($(this));"/>&nbsp;Migrate from MyNewspaper version 3
            <br/><br/>
            <span class="comment">
              Note that <i>import from OPML</i> or <i>import for Google Reader</i> take a while (approx. 1 sec per feed).
              You will also be able to add, edit, delete or import more feeds from other OPML files afterwards.
            </span>
            <br/><br/><br/>
            <center><input type="submit" value="Start MyNewspaper" onclick="return check_file();"/></center>
          </form>
        </p>
      </div>
    </div>
  </div>

</center></body>
</html>
