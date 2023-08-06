&nbsp;
<div class="item sgroup">
  <a onclick="go('h/0/0');"><img src="/images/home.png"/>&nbsp;Home</a>
</div>
<div class="item sgroup">
  <a onclick="go('t/0/-1');"><img src="/images/summary.png"/>&nbsp;Folders</a>
</div>
<div class="item sgroup">
  <a onclick="go('f/0/0');"><img src="/images/folder.png"/>&nbsp;Archive</a>
</div>
<div class="item sgroup">
  <a onclick="go('s/0/0');"><img src="/images/search.png"/>&nbsp;Search</a>
</div>
&nbsp;
<div class="item sgroup">
  <a onclick="go('a/0/1');"><img src="/images/rss.png"/>&nbsp;All items
    <span class="num">{{'%d' % num_unread if num_unread>0 else ''}}</span>
  </a>
</div>
%for g in gs:
<div class="item group">
  <img class="btn" src="/images/btn_collapsed.png"/>
  <a onclick="go('g/{{g.gid}}/1');">{{g.name}}
    <span class="num">{{'%d' % g.num_unread if g.num_unread>0 else ''}}</span>
  </a>
</div>
<div class="group_children">
  %for f in g.get_feeds():
  <div class="item feed">
    <a onclick="go('f/{{f.fid}}/1');"><img src="/favicon/{{f.fid}}" width="14" height="14"/>&nbsp;{{f.name}}
      <span class="num">{{'%d' % f.num_unread if f.num_unread>0 else ''}}</span>
    </a>
  </div>
  %end
</div>
%end
&nbsp;
