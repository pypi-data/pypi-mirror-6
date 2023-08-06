<div id="home">
  <h1>Folders&nbsp;&nbsp;&nbsp;<span>{{len(gs)}} folders</span></h1>
  <div class="actions">
    <a onclick="group_new();">new folder</a>
    <a>stats</a>
    <a onclick="update_feeds(-1);">update feeds</a>
  </div>

  <table id="summary_tbl">
    <thead>
      <tr class="header">
        <th class="name">Folder name</th>
        <th class="nums2">#</th>
        <th class="nums"><img src="/images/st_unread.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_starred.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_later.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_archived.png" width="18" height="18"/></th>
        <th class="nums"><img src="/images/st_all.png" width="18" height="18"/></th>
      </tr>
    </thead>
    <tbody>
      %if len(gs) == 0:
      <tr class="row"><td align="center" colspan="6" height="40">No folders created</td></tr>
      %else:
      %for g in gs:
      <tr class="row" title="Drag & drop the row to sort">
        <td class="name">
          <a onclick="summary_group({{g.gid}});" class="name" name="{{g.gid}}">
            <img src="/images/folder.png" width="14" height="14"/>{{g.name}}
          </a>
        </td>
        <td class="nums2"><a onclick="summary_group({{g.gid}});" class="name">{{len(g.get_feeds(False, False))}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/1" % g.gid}}');">{{g.num_unread}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/2" % g.gid}}');">{{g.num_starred}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/3" % g.gid}}');">{{g.num_later}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/4" % g.gid}}');">{{g.num_archived}}</a></td>
        <td class="nums"><a onclick="show_articles('{{"g/%d/0" % g.gid}}');">{{g.num_total}}</a></td>
      </tr>
      %end
      %end
    </tbody>
    <tfoot>
      <tr class="totals">
        <td class="name"><a class="total">Total</a></td>
        <td class="nums2">{{num_feeds}}</td>
        <td class="nums"><a onclick="show_articles('a/0/1');">{{nums[1]}}</a></td>
        <td class="nums"><a onclick="show_articles('a/0/2');">{{nums[2]}}</a></td>
        <td class="nums"><a onclick="show_articles('a/0/3');">{{nums[3]}}</a></td>
        <td class="nums"><a onclick="show_articles('a/0/4');">{{nums[4]}}</a></td>
        <td class="nums"><a onclick="show_articles('a/0/0');">{{nums[0]}}</a></td>
      </tr>
    </tfoot>
  </table>

  <br/><br/>  
</div>
