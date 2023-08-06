<div id="topbar">
  <a onclick="go('s/1')"><img src="/images/mob_back.png"/></a>
  %if num_query > 0:
  <span class="text">{{title}}&nbsp;&nbsp;&ndash;&nbsp;&nbsp;{{num_query}} of {{num_total}} articles</span>
  %else:
  <span class="text">{{title}}</span>
  %end
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
</div>

<div id="articles">
%if num_query > 0:
  %for a in arts:
  <div class="art">
    <div class="mnhdr">
      %st = 0 if state==1 else a.state # show unread -> preselect delete
      <img src="/images/{{icons[st]}}" name="{{a.aid}}" alt="{{st}}" class="icon" width="32" height="32"/>
      <span class="feedname">{{a.feedname}}</span>
      <img src="/images/circle.png" class="icon2" width="32" height="32"/>
      <span class="date2">{{a.timestamp}}</span>
    </div>
    <div class="mntitle">
      <a href="{{a.url}}" class="title" target="_blank">{{!a.title}}</a>
      <span class="summary">&nbsp;&ndash;&nbsp;{{a.summary}}</span>
    </div>
  </div>
  %end
%else:
  <div class="message">No articles</div>
%end
</div>

<div id="bottombar">
  <span style="color: #333333;">gjy</span>
  <div class="btns">
  %if num_query < num_total:
  <a id="btn_loadall" class="btn"><span>Load all</span></a>
  %end
  %if num_query != 0:
  <a id="btn_process" class="btn"><img src="/images/mob_process.png"/></a>
  %end
  </div>
</div>
