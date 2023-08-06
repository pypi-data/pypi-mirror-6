// Copyright (C) 2005-14  Iñigo Serna
// This file belongs to "MyNewspaper" application.
// Time-stamp: <2013-09-15 22:35:14 inigo>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


//////////////////////////////////////////////////////////////////////////
// Globals
var wis = "s/1";
var ST_ICONS = ['st_all.png', 'st_unread.png', 'st_starred.png', 'st_later.png', 'st_archived.png'];
var imgs_state = ['st_delete.png', 'st_unread.png', 'st_starred.png', 'st_later.png', 'st_archived.png'];
var $tmp = null;
var scrollY = 0;
var arts = null;


//////////////////////////////////////////////////////////////////////////
// Sidebar
function go(l_wis) {
    wis = l_wis;
    if (wis[0] == 's') {
        var st = parseInt(wis.substring(2));
        summary(st);
    } else if (wis[0] == 'a' || wis[0] == 'g' || wis[0] == 'f') {
        show_articles(wis);
    }
}


function activate_topbar_popups() {
    $("#topbar").find(".btn_popup").click(function(ev) {
        var $popup = $(this).find("div.popup");
        if ($popup.is(':visible')) {
            $popup.fadeOut();
       	} else {
            var h = $popup.outerHeight();
            var y = ev.clientY + h;
            var offsetY = y > window.innerHeight ? -h : $(this).innerHeight();
            $popup.css("top", offsetY).fadeIn();
        }
    }).mouseleave(function () {
        var $popup = $(this).find("div.popup");
        if ($popup.is(':visible'))
            $popup.fadeOut();
    });
}

function summary(st) {
    $("#contents").empty().append(div_loading);
    $("#contents").load("/ajax/mob_load_summary/" + st, function() {
        $("body").addClass("dark");
        // toolbar
        $("#topbar img.st_icon").attr('src', "/images/" + ST_ICONS[st]);
        activate_topbar_popups();
        $("#popup_show a").click(function() {
            $("#popup_show").parent().prev().trigger('mouseleave');
            var st_new = parseInt($(this).attr('name'));
            if (st != st_new) {
                $("body").removeClass("dark");
                summary(st_new);
                return false;
            }
        });
        // folders and feeds
        $("#summary .group").click(function() {
            $gfeeds = $(this).next();
            if ($gfeeds.attr('class') != 'group_children')
                return;
            $(this).find("img.btn").attr('src', "/images/btn_" + ($gfeeds.is(":hidden") ? "expanded" : "collapsed") + ".png");
            $gfeeds.toggle();
            return false;
        });
        $("#summary a.num").click(function() {
            go($(this).attr('name'));
            return false;
        });
    });
}


function show_articles(l_wis, loadall) {
    loadall = loadall ? 1 : 0;
    $("body").removeClass("dark");
    $("#contents").empty().append(div_loading);
    $("#contents").load("/ajax/mob_load_articles/" + l_wis + "/" + loadall, function() {
        bind_articles_actions(l_wis);
    });
}


function bind_articles_actions(l_wis) {
    var st = parseInt(l_wis.substr(-1));
    // toolbar
    $("#topbar img.st_icon").attr('src', "/images/" + ST_ICONS[st]);
    activate_topbar_popups();
    $("#popup_show a").click(function() {
        $("#popup_show").parent().prev().trigger('mouseleave');
        var st_new = parseInt($(this).attr('name'));
        if (st != st_new) {
            var l_wis2 = l_wis.substring(0, l_wis.length-1) + st_new;
            go(l_wis2);
            return false;
        }
    });
    $("#btn_loadall").click(function() { show_articles(l_wis, true); });
    $("#btn_process").click(function() { process_arts(wis); });
    // articles
    var $popup_states = $("<div class='states'><ul><li><a name='0'><img src='/images/st_delete.png' width='32' height='32'/>Delete</a></li><li><a name='1'><img src='/images/st_unread.png' width='32' height='32'/>Unread</a></li><li><a name='2'><img src='/images/st_starred.png' width='32' height='32'/>Starred</a></li><li><a name='3'><img src='/images/st_later.png' width='32' height='32'/>Later</a></li><li><a name='4'><img src='/images/st_archived.png' width='32' height='32'/>Archived</a></li></ul></div>")
        .popup(true).appendTo("#articles");
    $popup_states.find('a').click(function() {
        var st = $(this).attr('name');
        $popup_states.data('art').find("img.icon").attr({src: '/images/'+imgs_state[st], alt: st});
        $.popup.off($popup_states);
        return false;
    });
    var $popup_actions = $("<div class='actions'><ul><li><a id='openlink'>Open link in new tab</a></li><li><a>Send as email</a></li><li><a>Save to Pocket</a></li></ul></div>")
        .popup(false).appendTo("#articles");
    $popup_actions.find('#openlink').click(function() {
        window.open($popup_actions.data('art').find(".mntitle a").attr('href'), "_blank");
        $.popup.off($popup_actions);
        return false;
    });
    $("#articles .mnhdr img.icon").click(function() {
        $.popup.off($popup_actions);
        $.popup.toggle($popup_states, $(this));
        return false;
    });
    $("#articles .mnhdr img.icon2").click(function() {
        $.popup.off($popup_states);
        $.popup.toggle($popup_actions, $(this));
        return false;
    });
    $("#articles .mntitle a").click(function() {
        if ($popup_states.is(':visible')) { $.popup.off($popup_states); }
        if ($popup_actions.is(':visible')) { $.popup.off($popup_actions); }
        return false;
    });
    $("#articles .mntitle").click(function() {
        if ($popup_states.is(':visible') || $popup_actions.is(':visible')) {
            $.popup.off($popup_states);
            $.popup.off($popup_actions);
        } else {
            $tmp = $("#contents").clone();
            scrollY = $(document).scrollTop();
            arts = new Array();
            $("#articles .art:visible .mnhdr img.icon").each(function(idx, img) {
                arts[idx] = parseInt($(this).attr('name'));
            });
            var aid = parseInt($(this).parent().find(".mnhdr img.icon").attr('name'));
            load_article_view(aid);
        }
    });
}


function process_arts(wis) {
    if (!confirm('Process articles?'))
        return;
    var arts = new Array();
    $("#articles .art:visible .mnhdr img.icon").each(function(idx, img) {
        arts[idx] = $(this).attr('name') + ':' + $(this).attr('alt');
    });
    arts = arts.join(',');
    if (!arts)
	    return;
    $("#contents").empty().append(div_processing);
    $.post("/ajax/process_articles", {"arts": arts})
        .done(function() {
            show_articles(wis);
        })
	    .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR processing articles</div>")
        });
}


function load_article_view(aid) {
    var idx = arts.indexOf(aid);
    $("#contents").empty().append(div_loading);
    $("#contents").load("/ajax/mob_load_article/" + aid, function() {
        $("#topbar span.idx").text((idx+1) + " of " + arts.length);
        $("#btn_close").click(function() {
            $("body").empty().append($tmp);
            $tmp = null;
            bind_articles_actions(wis);
            $(document).scrollTop(scrollY);
            return false;
        });
        $("#btn_prev").click(function() {
            if (idx==0)
                return;
            aid = arts[idx-1];
            load_article_view(aid);
            return false;
        });
        $("#btn_next").click(function() {
            if (idx==arts.length-1)
                return;
            aid = arts[idx+1];
            load_article_view(aid);
            return false;
        });
    });

}


//////////////////////////////////////////////////////////////////////////
// Dialogs & messages
var div_loading = "<div class='loading'><div>Loading...</div><br/><img src='/images/loading2.gif' /></div>";
var div_processing = "<div class='loading'><div>Processing...</div><br/><img src='/images/loading2.gif' /></div>";


//////////////////////////////////////////////////////////////////////////
// My own modal dialog
(function($) {
     $.fn.popup = function(alignleft) {
         $(this)
             .data('alignleft', alignleft)
             .mouseleave(function () { $.popup.off($(this)); });
         return $(this);
     };
     // static functions
     $.popup = $.popup || {};
     $.popup.toggle = function($dlg, $obj) {
         $dlg.is(':visible') ? $.popup.off($dlg) : $.popup.on($dlg, $obj);
     };
     $.popup.on = function($dlg, $obj) {
         $dlg.data('art', $obj.parent().parent());
         var x = $dlg.data('alignleft') ? 5 : $(window).width() - $dlg.outerWidth() - 5;
         var y = $obj.position().top + $obj.outerHeight() + 3;
         if (y+$dlg.outerHeight() > + $(window).scrollTop()+$(window).height())
             y = $(window).scrollTop() + $(window).height() - $dlg.outerHeight() - 5;
         $dlg.css({left: x, top: y}).fadeIn("fast")
     };
     $.popup.off = function($dlg) {
         $dlg.data('art', null);
         $dlg.fadeOut();
     };
})(jQuery);


//////////////////////////////////////////////////////////////////////////
