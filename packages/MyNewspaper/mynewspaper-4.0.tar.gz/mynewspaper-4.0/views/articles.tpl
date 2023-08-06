%if len(arts) > 0:
  %for a in arts:
  <div class="art">
    <div class="mnhdr1">
      %if state == 1: # show unread -> preselect delete
      <img src="/images/{{icons[0]}}" name="{{a.aid}}" alt="0" class="icon"/>
      %else:
      <img src="/images/{{icons[a.state]}}" name="{{a.aid}}" alt="{{a.state}}" class="icon"/>
      %end
      <div class="feedname">{{a.feedname}}</div>
      <img src="/favicon/{{a.fid}}" width="14" height="14"/>
      <div class="wrapper">
        <div class="title_container">
          <a href="{{a.url}}" class="title" target="_blank">{{!a.title}}</a>
          <div class="summary">&nbsp;&ndash;&nbsp;{{a.summary}}</div>
        </div>
      </div>
      <div class="date1">{{a.timestamp}}</div>
    </div>
    <div class="content_container">
      <div class="mnhdr2">
        <a href="{{a.url}}" class="title2" target="_blank">{{!a.title}}</a>
        <div>From <a href="{{a.feedlink}}" class="feedname2" target="_blank">{{a.feedname}}</a>, at <span class="date2">{{a.timestamp2}}</span></div>
      </div>
      <div class="content">{{!a.contents}}</div>
    </div>
  </div>
  %end
%else:
  <div class="message">No articles</div>
%end
