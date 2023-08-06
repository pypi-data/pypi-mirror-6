<div id="home">
  <h1>{{f.name}}</h1>
  <div class="actions">
    <a onclick="feed_edit({{f.fid}});">edit</a>
    <a onclick="feed_delete({{f.fid}}, {{f.gid}});">delete</a>
    <a>stats</a>
    <a onclick="update_feed({{f.fid}});">update</a>
  </div>
  <br/>

  <table id="summary_tbl_feed">
    <tr><td></td><td></td></tr>
    <tr><td class="field">Feed name:</td><td><img src="/favicon/{{f.fid}}" width="16" height="16"/ class="favicon">{{f.name}}</td></tr>
    <tr><td class="field">URL:</td><td><a href="{{f.url}}" target="_blank">{{f.url}}</a></td></tr>
    <tr><td class="field">Home page:</td><td><a href="{{f.link}}" target="_blank">{{f.link}}</a></td></tr>
    <tr><td class="field">Folder:</td><td><a onclick="summary_group({{f.gid}});">{{groupname}}</a></td></tr>
    <tr><td class="field">State:</td><td>{{feedstate}}</td></tr>
    <tr><td class="field">Articles:</td>
      <td>
        <a onclick="show_articles('{{"f/%d/1" % f.fid}}');">{{f.num_unread}}<img src="/images/st_unread.png"/></a>
        <a onclick="show_articles('{{"f/%d/2" % f.fid}}');">{{f.num_starred}}<img src="/images/st_starred.png"/></a>
        <a onclick="show_articles('{{"f/%d/3" % f.fid}}');">{{f.num_later}}<img src="/images/st_later.png"/></a>
        <a onclick="show_articles('{{"f/%d/4" % f.fid}}');">{{f.num_archived}}<img src="/images/st_archived.png"/></a>
        <a onclick="show_articles('{{"f/%d/0" % f.fid}}');">{{f.num_total}}<img src="/images/st_all.png"/></a>
      </td>
    </tr>
    <tr><td class="field">Last update:</td><td>{{lastupdate}}</td></tr>
  </table>

  <br/><br/>
</div>
