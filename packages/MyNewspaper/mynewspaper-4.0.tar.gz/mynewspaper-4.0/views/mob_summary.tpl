<div id="topbar">
  <span class="bigtext">MyNewspaper Summary</span>
  <span class="btn_popup"><img class="st_icon" src="/images/st_unread.png" width="40" height="40"/>
    <div class="popup">
      <ul id="popup_show">
        <li><a name="0"><img src="/images/st_all.png" width="32" height="32"/>All items</a></li>
        <li><a name="1"><img src="/images/st_unread.png" width="32" height="32"/>Unread</a></li>
        <li><a name="2"><img src="/images/st_starred.png" width="32" height="32"/>Starred</a></li>
        <li><a name="3"><img src="/images/st_later.png" width="32" height="32"/>Later</a></li>
        <li><a name="4"><img src="/images/st_archived.png" width="32" height="32"/>Archived</a></li>
      </ul>
    </div>
  </span>
  <div class="btns">
    <a id="btn_settings" class="btn"><img src="/images/mob_settings.png"/></a>
  </div>
</div>

%ATTR_ST = ['num_total', 'num_unread', 'num_starred', 'num_later', 'num_archived']
<div id="summary">
  <div class="group">
    <img src="/images/rss.png" width="32" height="32"/>
    <span>All items</span>
    <a class="num" name="a/0/{{st}}">{{num}}</a>
  </div>
  %for g in gs:
  %if st==0 or eval('g.'+ATTR_ST[st])!=0:
  <div class="group">
    <img class="btn" src="/images/btn_collapsed.png" width="32" height="32"/>
    <span>{{g.name}}</span>
    <a class="num" name="g/{{g.gid}}/{{st}}">{{eval('g.'+ATTR_ST[st])}}</a>
  </div>
  <div class="group_children">
    %for f in g.get_feeds():
    %if st==0 or eval('f.'+ATTR_ST[st])!=0:
    <div class="feed">
      <img src="/favicon/{{f.fid}}" width="32" height="32"/>
      <span>{{f.name}}</span>
      <a class="num" name="f/{{f.fid}}/{{st}}">{{eval('f.'+ATTR_ST[st])}}</a>
    </div>
    %end
    %end
  </div>
  %end
  %end
</div>
