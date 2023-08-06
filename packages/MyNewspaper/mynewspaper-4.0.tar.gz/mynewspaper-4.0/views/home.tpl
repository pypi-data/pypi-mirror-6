<div id="home">
  <h1>Home</h1>

  <div class="admin_container">
    <div class="section">
      <ul><h3>Feeds and folders</h3>
        <li><a onclick="feed_new(-1);">Add subscription</a></li>
        <li><a onclick="summary_group(-1);">Folders</a></li>
        <li><a onclick="goto_unread();">Unread posts</a></li>
        <li><a onclick="update_feeds(-1);">Update feeds</a></li>
      </ul>
    </div>
    
    <div class="section">
      <ul><h3>Administration</h3>
        <li><a onclick="import_opml();">Import OPML</a></li>
        <li><a onclick="export_opml_db();">Export OPML or Database</a></li>
        <li><a href="">Settings</a></li>
        <li><a onclick="clean_data();">Clean data</a></li>
      </ul>
    </div>

    <div class="section">
      <ul><h3>Reports</h3>
        <li><a href="">Disabled feeds ({{nfeeds[1]}})</a></li>
        <li><a href="">Broken feeds ({{nfeeds[2]}})</a></li>
        <li><a href="">Inactive feeds ({{nfeeds[3]}})</a></li>
      </ul>
    </div>
    
    <div class="section">
      <ul><h3>Help</h3>
        <li><a href="/docs/readme.html" target="_blank">Documentation</a></li>
        <li><a onclick="help_keys();">Keyboard shortcuts</a></li>
        <li><a href="/docs/agpl-3.0.html" target="_blank">License</a></li>
        <li><a href="">Donate</a></li>
      </ul>
    </div>
  </div>

  <div class="sum_home">
    Subscribed to {{nfeeds[0]}} feeds, distributed in {{num_groups}} folders<br/>
    Last update: {{lastupdate}}<br/>
    <img src="/images/st_all.png" width="14" height="14"/>&nbsp;Total {{nums[0]}} articles stored<br/>
    <img src="/images/st_unread.png" width="14" height="14"/>&nbsp;{{nums[1]}} unread<br/>
    <img src="/images/st_starred.png" width="14" height="14"/>&nbsp;{{nums[2]}} starred<br/>
    <img src="/images/st_later.png" width="14" height="14"/>&nbsp;{{nums[3]}} saved for later<br/>
    <img src="/images/st_archived.png" width="14" height="14"/>&nbsp;{{nums[4]}} archived
  </div>
  
</div>
