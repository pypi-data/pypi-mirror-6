<div id="home">
  <h1>{{title}}&nbsp;&nbsp;&nbsp;<span>{{len(fs)}} subscriptions</span></h1>
  <div class="actions">
    <a onclick="feed_new({{gid}});">add subscription</a>
    <a onclick="group_edit({{gid}}, '{{groupname}}');">rename folder</a>
    <a onclick="group_delete({{gid}});">delete folder</a>
    <a>stats</a>
    <a onclick="update_feeds({{gid}});">update feeds</a>
  </div>

  <table id="summary_tbl">
    <thead>
      <tr class="header">
        <th class="name">Feed name</th>
        <th class="nums"><img src="/images/st_unread.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_starred.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_later.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_archived.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_all.png" width="18" height="18"/></th>
      </tr>
    </thead>
    <tbody>
      %if len(fs) == 0:
      <tr class="row"><td align="center" colspan="6" height="40">No feeds here</td></tr>
      %else:
      %for f in fs:
      <tr class="row" title="Drag & drop the row to sort">
        <td class="name">
          %if f.state == 2:
              % specialcls = ' disabled'
          %elif f.state == 3:
              % specialcls = ' broken'
          %else:
              % specialcls = ''
          %end
          <a onclick="summary_feed({{str(f.fid)}});" class="name{{specialcls}}" name="{{f.fid}}">
            <img src="/favicon/{{f.fid}}" width="14" height="14"/>{{f.name}}
          </a>
        </td>
        <td class="nums"><a onclick="show_articles('{{"f/%d/1" % f.fid}}');">{{f.num_unread}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"f/%d/2" % f.fid}}');">{{f.num_starred}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"f/%d/3" % f.fid}}');">{{f.num_later}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"f/%d/4" % f.fid}}');">{{f.num_archived}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"f/%d/0" % f.fid}}');">{{f.num_total}}</a></td>
      </tr>
      %end
      %end
    </tbody>
    <tfoot>
      <tr class="totals">
        <td class="name"><a onclick="summary_group(-1);" class="total">Total</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/1" % gid}}');">{{nums[1]}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/2" % gid}}');">{{nums[2]}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/3" % gid}}');">{{nums[3]}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/4" % gid}}');">{{nums[4]}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/0" % gid}}');">{{nums[0]}}</a></td>
      </tr>
    </tfoot>
  </table>
  
  <br/><br/>
</div>
