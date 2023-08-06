<div id="topbar">
  <a id="btn_close"><img src="/images/mob_back.png"/></a>
  <span class="text">Feed: {{art.feedname}}</span>
  <div class="btns">
    <a id="btn_prev" class="btn"><img src="/images/mob_prev.png"/></a>
    <span class="text idx">1 of 50</span>
    <a id="btn_next" class="btn"><img src="/images/mob_next.png"/></a>
  </div>
</div>

<div id="article">
  <div class="mnhdr">
    <a href="{{art.url}}" class="title" target="_blank">{{!art.title}}</a>
    <div>From <span class="feedname">{{art.feedname}}</span>, at <span class="date">{{art.timestamp2}}</span></div>
  </div>
  <div class="content">{{!art.contents}}</div>
</div>
