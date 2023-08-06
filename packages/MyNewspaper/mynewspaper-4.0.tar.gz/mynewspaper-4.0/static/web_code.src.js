// Copyright (C) 2005-14  Iñigo Serna
// This file belongs to "MyNewspaper" application.
// Time-stamp: <2013-12-03 17:12:01 inigo>
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
var viewtype = 0; // 0..1
var view_imgs = 1; // 0..1
var wis = "h/0/0";
var offset = DEFAULT_OFFSET = 0;
var limit = DEFAULT_LIMIT = 50;
var sorttype = 1; // 0..4
var num_arts = 0;


//////////////////////////////////////////////////////////////////////////
// Main
function mn_load(l_wis) {
    $("#img_sb").css("cursor", "pointer").click(function() { sidebar_toggle($(this)); });
    $("#img_refresh").css("cursor", "pointer").click(function() { sidebar_load(); go(wis); });
    $("#sidebar").css({height: $(window).height()-42+'px'});
    sidebar_load();
    go(l_wis);
    $(window).keydown(function(ev) {
        if (ev.altKey)
            return true;
        var $art = $("#articles .cursor:eq(0)");
        return $art.length==1 ? handle_arts_keys(ev, $art) : handle_global_keys(ev);
    });
    $(window).resize(function() {
        $("#sidebar").css({height: $(window).height()-42+'px'});
        if ($("#articles .cursor:eq(0)").length==1)
            calc_art_titlewrap_width();
    });
}

function go(l_wis) {
    wis = l_wis;
    if (wis[0] == 'h') {
        if (wis[2] == '0')
            home();
    } else if (wis[0] == 't') {
        var id = parseInt(wis.substring(4));
        if (wis[2] == '0')
            summary_group(id);
        else if (wis[2] == '1')
            summary_feed(id);
    } else if (wis[0] == 'a' || wis[0] == 'g' || wis[0] == 'f') {
        show_articles(wis);
    } else if (wis[0] == 's') {
        search();
    }
}

function handle_global_keys(ev) {
    var val = false;
    if (ev.ctrlKey || ev.altKey)
        return true;
    switch (ev.keyCode) {
        case 27: // esc
            sidebar_toggle();
            break;
        case 72: // h
            home();
            break;
        case 70: // f
            summary_group(-1);
            break;
        case 55: // /
            search();
            break;
        case 82: // r
            sidebar_load();
            go(wis);
            break;
        case 85: // u
            goto_unread();
            break;
        case 222: // ? in firefox
        case 191: // ? in google chrome
            help_keys();
            break;
        case 38: // cursorup
            $("#contents").scrollTop($("#contents").scrollTop() - 25);
            break;
        case 40: // cursordown
            $("#contents").scrollTop($("#contents").scrollTop() + 25);
            break;
        case 33: // pageup
            $("#contents").scrollTop($("#contents").scrollTop() - $("#contents").height());
            break
        case 34: // down
            $("#contents").scrollTop($("#contents").scrollTop() + $("#contents").height());
            break
        default:
            val = true;
    }
    return val;
}


//////////////////////////////////////////////////////////////////////////
// Sidebar
function sidebar_load(sel) {
    $("#sidebar").empty();
    $("#sidebar").load("/ajax/sidebar_load", function() {
        // collapse/expand groups
        $("#sidebar .group img.btn").click(function() {
            $gfeeds = $(this).parent().next();
            $(this).attr('src', "/images/btn_" + ($gfeeds.is(":hidden") ? "expanded" : "collapsed") + ".png");
            $gfeeds.toggle();
            return false;
        });
        // select item when clicked
        $("#sidebar a").click(function() {
            $("#sidebar .item").removeClass("selected");
            $(this).parent().addClass("selected");
        });
        // select item
        if(!(typeof(sel)==='undefined'))
            $('#sidebar .item > a[onclick="' + sel.replace(/'/g, "\\'") + '"]').parent().addClass("selected");
    });
}

function sidebar_toggle(img_sb) {
    img_sb = img_sb || $("#img_sb");
    if ($("#sidebar").is(":hidden")) {
        $("#sidebar").fadeIn('slow', function() {
            img_sb.attr({src: "/images/sidebar_off.png"});
        });
        $("#contents").css({marginLeft: '230px'});
    } else {
        $("#sidebar").fadeOut('slow', function() {
            $("#contents").css({marginLeft: '0px'});
            img_sb.attr({src: "/images/sidebar_on.png"});
        });
        $("#contents").css({marginLeft: '0px'});
    }
    calc_art_titlewrap_width();
}


//////////////////////////////////////////////////////////////////////////
// Home
function home() {
    wis = "h/0/0";
    $("#sidebar .item").removeClass("selected");
    $("#sidebar .item:eq(0)").addClass("selected");
    $("#contents").empty().append(div_loading);
    $("#contents").load("/ajax/home");
}

function summary_group(gid) {
    wis = "t/0/" + gid;
    $("#sidebar .item").removeClass("selected");
    $("#sidebar .item:eq(1)").addClass("selected");
    $("#contents").empty().append(div_loading);
    $("#contents").load("/ajax/summary_group/" + gid, function() {
        $("#summary_tbl tbody")
            .sortable({containment: $("#summary_tbl"), axis: 'y', cursor: 'move', distance: 10,
                       placeholder: 'sort-highlight', opacity: 0.5,
                       update: function(event, ui) {
                           $("#summary_tbl tr").css({opacity: 1});
                           var items = new Array();
                           $("#summary_tbl tbody td.name a").each(function(idx, elm) {
                               items[idx] = elm.name; });
                           items = items.join(',');
                           $.post("/ajax/sort_items", {"gid": gid, "order": items})
                               .done(function() {
                                   sidebar_load();
                                   summary_group(gid);
                               })
                               .fail(function() {
                                   $("#contents").empty().append("<div class='error'>ERROR sorting</div>")
                               });
                      }})
            .disableSelection();
    });
}

function summary_feed(fid) {
    wis = "t/1/" + fid;
    $("#sidebar .item").removeClass("selected");
    $("#sidebar .item:eq(1)").addClass("selected");
    $("#contents").empty().append(div_loading);
    $("#contents").load("/ajax/summary_feed/" + fid);
}

function search(){
    wis = "s/0/0";
    $("#sidebar .item").removeClass("selected");
    $("#sidebar .item:eq(3)").addClass("selected");
    $("#contents").empty().append("<div class='message'>Search</div>")
}

function goto_unread() {
    $("#sidebar .item").removeClass("selected");
    $("#sidebar .item:eq(4)").addClass("selected");
    show_articles("a/0/1");
    window.scroll(0, 0);
}

function import_opml() {
    var $dia = $("<div class='title'>Import OPML</div>" +
                 "<form id='import_opml' action='/import_opml' method='post' enctype='multipart/form-data'>" +
                   "<table><tbody><tr> " +
                     "<td>OPML file:</td><td><input type='file' name='opmlfile'/></td>" +
                   "</tr></tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Select the OPML file with your feeds subscriptions</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='btn_import_opml' value='Import'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Import OPML");
    $dia.find("input[name='btn_import_opml']").click(function() {
        var filename = $("#dialog input[name='opmlfile']").val();
        if (filename == '') {
            alert('Please, select a file');
            return false;
        }
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_importing);
        return true;
    });
}

function export_opml_db() {
    var $dia = $("<div class='title'>Export</div>" +
                 "<form id='export' action='/export' method='post' enctype='multipart/form-data'>" +
                   "<table><tbody>" +
                     "<tr><td><input type='radio' name='export' value='opml' checked />&nbsp;Export subscriptions as an OPML file</td></tr>" +
                     "<tr><td><input type='radio' name='export' value='db' />&nbsp;Export Database with all information</td></tr>" +
                   "</tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Select what data you want to export</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='btn_export' value='Export'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Export");
    $dia.find("input[name='btn_export']").click(function() {
        $.modaldialog.end($dia);
        return true;
    });
}

function clean_data() {
    var $dia = $("<div class='title'>Clean data</div>" +
                 "<form id='export' action='/clean_data' method='post' enctype='multipart/form-data'>" +
                   "<table><tbody>" +
                     "<tr><td><input type='radio' name='clean' value='vacuum' checked/>&nbsp;Compact database (vacuum)</td></tr>" +
                     "<tr><td><input type='radio' name='clean' value='cache' />&nbsp;Remove old entries from cache (> 3 months)</td></tr>" +
                   "</tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Select what data you want to clean</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='btn_clean' value='Clean'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Clean data");
    $dia.find("input[name='btn_clean']").click(function() {
        if (!confirm('Are you sure?')) {
            $.modaldialog.end($dia);
            return false;
        }
        var val = $("#dialog input[name='clean']:checked").val();
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_processing);
        $.post("/clean/" + val)
            .done(function() {
                sidebar_load();
                home();
            })
            .fail(function(err) {
                $("#contents").empty().append("<div class='error'>ERROR cleaning</div>");
            });
        return false;
    });
}

function help_keys() {
    $("<div id='help_keys' tabindex='3'/>").load("/ajax/help_keys", function() {
        var $dlg = $(this).modaldialog3().attr("title", "Keyboard Shortcuts");
        $(this).find("a.btn_close").click(function() { $.modaldialog3.end($dlg); });
    });
}


//////////////////////////////////////////////////////////////////////////
// Actions
function update_feeds(gid) {
    if (!confirm('This may take a long time. Are you sure?'))
        return;
    // $("#contents").empty().append(div_updating);
    $.post("/ajax/update_feeds/" + gid)
        .done(function() {
            sidebar_load();
        })
        .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR updating feeds</div>")
        });
}

function update_feed(fid) {
    $("#contents").empty().append(div_updating);
    $.post("/ajax/update_feed/" + fid)
        .done(function() {
            sidebar_load();
            summary_feed(fid);
        })
        .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR updating feed</div>")
        });
}

function group_new() {
    var $dia = $("<div class='title'>New Folder</div>" +
                 "<form id='group_new' action='' method='post'>" +
                   "<table><tbody><tr> " +
                     "<td>Name:</td><td><input type='text' name='groupname' size='30'/></td>" +
                   "</tr></tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Type the name for the new folder</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='group_new' value='Add folder'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "New folder");
    $dia.find("input[name='group_new']").click(function() {
        var groupname = $("#dialog input[name='groupname']").val();
        if (groupname == '') {
            $.modaldialog.error($dia, 'Please specify a name for the folder');
            return false;
        }
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_processing);
        $.post("/ajax/group_new", {"groupname": groupname})
            .done(function() {
                sidebar_load();
                summary_group(-1);
            })
            .fail(function() {
                $("#contents").empty().append("<div class='error'>ERROR adding new folder</div>")
            });
        return false;
    });
}

function group_edit(gid, groupname) {
    if (gid == 0) {
        alert("You should not rename this folder");
        return false;
    }
    var $dia = $("<div class='title'>Rename Folder</div>" +
                 "<form id='group_edit' action='' method='post'>" +
                   "<table><tbody><tr> " +
                     "<td>Name:</td><td><input type='text' name='groupname' value='" + groupname + "' size='30'/></td>" +
                   "</tr></tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Type the new name for the folder</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='group_edit' value='Rename folder'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Rename folder");
    $dia.find("input[name='group_edit']").click(function() {
        var newgroupname = $("#dialog input[name='groupname']").val();
        if (newgroupname == groupname) {
            $.modaldialog.end($dia);
            return false;
        }
        if (newgroupname == '') {
            $.modaldialog.error($dia, 'Please specify the new name for the folder');
            return false;
        }
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_processing);
        $.post("/ajax/group_edit", {"gid": gid, "groupname": newgroupname})
            .done(function(r) {
                if (r.errmsg) {
                    summary_group(gid);
                    alert("Error renaming folder!\n" + newgroupname + " " + r.errmsg + ".")
                    group_edit(gid, groupname)
                } else {
                    sidebar_load();
                    summary_group(gid);
                }
            })
            .fail(function() {
                $("#contents").empty().append("<div class='error'>ERROR renaming folder</div>")
            });
        return false;
    });
}

function group_delete(gid) {
    if (gid == 0) {
        alert("You should not delete this folder");
        return false;
    }
    var $dia = $("<div class='title'>Delete Folder</div>" +
                 "<form id='group_delete' action='' method='post'>" +
                   "<table><tbody><tr> " +
                     "<td><input type='checkbox' name='move_arts' checked>&nbsp;&nbsp;Move articles to Archive folder</td>" +
                   "</tr></tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Deleting the folder will remove all feeds as well</span><br/>" +
                   "<span class='comment'>Mark above option to save the posts in the special <b>Archive</b> folder</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='group_delete' value='Delete folder'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Delete folder");
    $dia.find("input[name='group_delete']").click(function() {
        var move_arts = $("#dialog :checkbox").get(0).checked ? 1 : 0;
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_processing);
        $.post("/ajax/group_delete", {"gid": gid, "move_arts": move_arts})
            .done(function() {
                sidebar_load();
                summary_group(-1);
            })
            .fail(function() {
                $("#contents").empty().append("<div class='error'>ERROR deleting folder</div>")
            });
        return false;
    });
}

function feed_new(gid) {
    var $dia = $("<div class='title'>Add Subscription</div>" +
                 "<form id='feed_new' action='' method='post'>" +
                   "<table><tbody><tr> " +
                     "<td>URL:</td><td><input type='text' name='feedurl' size='50'/></td>" +
                   "</tr></tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Type the URL for the new feed</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='feed_new' value='Add subscription'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Add subscription");
    $dia.find("input[name='feed_new']").click(function() {
        var feedurl = $("#dialog input[name='feedurl']").val();
        if (feedurl == '') {
            $.modaldialog.error($dia, 'Please specify feed URL');
            return false;
        }
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_processing);
        $.post("/ajax/feed_new", {"feedurl": feedurl, "gid": gid})
            .done(function(r) {
                if (r.errmsg) {
                    if (gid == -1)
                        home();
                    else
                        summary_group(gid);
                    alert("Error adding subscription!\n" + r.errmsg + ".")
                } else {
                    sidebar_load();
                    summary_feed(r.fid);
                }
            })
            .fail(function() {
                $("#contents").empty().append("<div class='error'>ERROR adding new subscription</div>")
            });
        return false;
    });
}

function feed_edit(fid) {
    if (fid == 0) {
        alert("You should not edit this 'Archive' feed");
        return false;
    }
    $.getJSON("/ajax/get_feed_edit_info/" + fid)
        .done(function(r) {
            var $dia = $("<div class='title'>Edit Feed</div>" +
                         "<form id='feed_edit' action='' method='post'>" +
                         "<table><tbody>" +
                           "<tr><td>Name:</td><td><input type='text' name='feedname' value='" + r.feedname + "' size='50'/></td></tr>" +
                            "<tr><td>URL:</td><td><input type='text' name='url' value='" + r.url + "' size='50'/></td></tr>" +
                           "<tr><td>Home page:</td><td><input type='text' name='link' value='" + r.link + "' size='50'/></td></tr>" +
                           "<tr><td>Folder:</td><td><select name='group'></select></td></tr>" +
                           "<tr><td>Enabled:</td><td><input type='checkbox' name='enabled' checked></td></tr>" +
                         "</tbody></table>" +
                         "<br/>" +
                         "<span class='comment'>Type the new information for the feed</span>" +
                         "<hr/>" +
                         "<div class='btns'>" +
                           "<input type='submit' name='feed_edit' value='Edit feed'/>" +
                           "<input type='submit' name='cancel' value='Cancel''/>" +
                         "</div>" +
                         "</form>").modaldialog().attr("title", "Edit feed");
            $.each(r.groups, function(i, g) {
                $("<option value='" + g.gid + "'>" + g.name + "</option>").appendTo("#dialog select[name='group']");
            });
            $("#dialog select[name='group'] option[value='" + r.gid + "']").attr("selected", "selected");
            $("#dialog :checkbox").get(0).checked = (r.state==1 ? true: false);
            $dia.find("input[name='feed_edit']").click(function() {
                var feedname = $("#dialog input[name='feedname']").val();
                var url = $("#dialog input[name='url']").val();
                var link = $("#dialog input[name='link']").val();
                var gid = $("#dialog select[name='group']").val();
                var state = $("#dialog :checkbox").get(0).checked ? 1 : 0;
                if (feedname==r.feedname && url==r.url && link==r.link && gid==r.gid && state==r.state) {
                    $.modaldialog.end($dia);
                    return false;
                }
                if (feedname == '') {
                    $.modaldialog.error($dia, 'Please specify the new name for the feed');
                    return false;
                }
                if (url == '') {
                    $.modaldialog.error($dia, 'Please specify a URL for the feed');
                    return false;
                }
                if (link == '') {
                    $.modaldialog.error($dia, 'Please specify the home page of the feed');
                    return false;
                }
                $.modaldialog.end($dia);
                $("#contents").empty().append(div_processing);
                $.post("/ajax/feed_edit", {"fid": fid, "feedname": feedname, "url": url, "link": link, "gid": gid, "state": state})
                    .done(function(r) {
                        if (r.errmsg) {
                            summary_feed(fid);
                            alert("Error editing feed!\n" + r.errmsg + ".")
                            feed_edit(fid)
                        } else {
                            sidebar_load();
                            summary_feed(fid);
                        }
                    })
                    .fail(function() {
                        $("#contents").empty().append("<div class='error'>ERROR editing feed</div>")
                    });
                return false;
            });
        })
        .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR editing feed</div>")
            return false;
        });
}

function feed_delete(fid, gid) {
    if (fid == 0) {
        alert("You should not delete this feed");
        return false;
    }
    var $dia = $("<div class='title'>Delete Feed</div>" +
                 "<form id='feed_delete' action='' method='post'>" +
                   "<table><tbody><tr> " +
                     "<td><input type='checkbox' name='move_arts' checked>&nbsp;&nbsp;Move articles to Archive folder</td>" +
                   "</tr></tbody></table>" +
                   "<br/>" +
                   "<span class='comment'>Mark above option to save the posts in the special <b>Archive</b> folder</span>" +
                   "<hr/>" +
                   "<div class='btns'>" +
                     "<input type='submit' name='feed_delete' value='Delete feed'/>" +
                     "<input type='submit' name='cancel' value='Cancel''/>" +
                   "</div>" +
                 "</form>").modaldialog().attr("title", "Delete feed");
    $dia.find("input[name='feed_delete']").click(function() {
        var move_arts = $("#dialog :checkbox").get(0).checked ? 1 : 0;
        $.modaldialog.end($dia);
        $("#contents").empty().append(div_processing);
        $.post("/ajax/feed_delete", {"fid": fid, "move_arts": move_arts})
            .done(function() {
                sidebar_load();
                summary_group(gid);
            })
            .fail(function() {
                $("#contents").empty().append("<div class='error'>ERROR deleting feed</div>")
            });
        return false;
    });
}


//////////////////////////////////////////////////////////////////////////
// Articles
function calc_art_titlewrap_width() {
    var ww = $("#articles .mnhdr").width() - 4 - 52 - $("#articles .icon").width() - $("#articles .feedname").width() - $("#articles .date1").width();
    $("#articles .wrapper").css("width", ww);
}

function build_actionbar() {
    var $actionbar = $('<div id="actionbar"><a id="btn_process" class="btn">&nbsp;Process&nbsp;</a><span class="btn_popup">Show&nbsp;[<span id="lbl_show"></span>]<img src="/images/popup.png"/><div class="popup"><ul id="popup_show"><li name="0"><img src="/images/st_all.png"/>All items</li><li name="1"><img src="/images/st_unread.png"/>Unread</li><li name="2"><img src="/images/st_starred.png"/>Starred</li><li name="3"><img src="/images/st_later.png"/>Later</li><li name="4"><img src="/images/st_archived.png"/>Archived</li></ul></div></span><span class="btn_popup">Filter by&nbsp;[<span id="lbl_filter"></span>]<img src="/images/popup.png"/><div class="popup"><ul id="popup_filter"><li name="0"><img src="/images/st_all.png"/>No filter</li><li name="1"><img src="/images/st_delete.png"/>To delete</li><li name="2"><img src="/images/st_unread.png"/>Unread</li><li name="3"><img src="/images/st_starred.png"/>Starred</li><li name="4"><img src="/images/st_later.png"/>Later</li><li name="5"><img src="/images/st_archived.png"/>Archived</li></ul></div></span><span class="btn_popup">Sort by&nbsp;[<span id="lbl_sort"></span>]<img src="/images/popup.png"/><div class="popup"><ul id="popup_sort"><li name="0">No sort</li><li name="1">Newer, then feed</li><li name="2">Older, then feed</li><li name="3">Feed, then newer</li><li name="4">Feed, then older</li></ul></div></span><span class="btns"><a id="btn_view" class="btn"><img /></a><a id="btn_imgs" class="btn"><img /></a></span><span class="btn_popup">Mark all as<img src="/images/popup.png"/><div class="popup"><ul id="popup_mark"><li name="0"><img src="/images/st_delete.png"/>To delete</li><li name="1"><img src="/images/st_unread.png"/>Unread</li><li name="2"><img src="/images/st_starred.png"/>Starred</li><li name="3"><img src="/images/st_later.png"/>Later</li><li name="4"><img src="/images/st_archived.png"/>Archived</li><li name="5"><img src="/images/st_restore.png"/>Restore state</li></ul></div></span></div>');
    $actionbar.find(".btn_popup").click(function(ev) {
        var $popup = $(this).find("div.popup");
        $popup.hide();
        var h = $popup.outerHeight();
        var y = ev.clientY + h;
        var offsetY = y > window.innerHeight ? -h : $(this).innerHeight();
        $popup.css("top", offsetY).toggle();
        $(this).addClass("btn_popup_selected");
    }).mouseleave(function () {
        $(this).removeClass("btn_popup_hover btn_popup_selected");
        var $popup = $(this).find("div.popup");
        if ($popup.is(':visible'))
            $popup.fadeOut("slow");
    }).mouseenter(function () {
        $(this).addClass("btn_popup_hover");
    });

    return $actionbar;
}

var imgs_state = ['st_delete.png', 'st_unread.png', 'st_starred.png', 'st_later.png', 'st_archived.png'];
function wis2st_str(l_wis) {
    var show_states = ['All items', 'Unread', 'Starred', 'Later', 'Archived'];
    return show_states[l_wis.substr(-1)];
}

function filter2str(filter) {
    var filter_types = ['No filter', 'To delete', 'Unread', 'Starred', 'Later', 'Archived'];
    return filter_types[filter];
}

function sort2str(sort) {
    var sort_types = ['No sort', 'Newer then feed', 'Older, then feed', 'Feed, then newer', 'Feed, then older'];
    return sort_types[sort];
}

function change_sort(newsort) {
    sorttype = newsort;
}

function change_view(newview) {
    viewtype = newview;
    if (viewtype == 0) {
        $("#actionbar #btn_view img").attr('src', '/images/btn_view_contents.png');
        $("#articles .content_container").hide();
        $("#articles .mnhdr1").removeClass("expanded");
    } else {
        $("#actionbar #btn_view img").attr('src', '/images/btn_view_list.png');
        $("#articles .content_container").show();
        $("#articles .mnhdr1").addClass("expanded");
    }
}

function change_filter(filter) {
    if (filter == 0) {
        $("#articles .art").show();
        $("#articles .mnhdr .num_hidden").empty();
    } else {
        var num_hidden = 0;
        $("#articles .mnhdr1 img.icon").each(function() {
            if (parseInt($(this).attr('alt')) == filter-1) { // delete=0, unread=1...
                $(this).parent().parent().show();
            } else {
                $(this).parent().parent().hide();
                num_hidden += 1;
            }
        });
        $("#articles .mnhdr .num_hidden").text(" (" + num_hidden + " filtered)");
    }
    $("#actionbar #lbl_filter").text(filter2str(filter));
    $("#articles .art").removeClass("cursor");
    $("#articles .art:visible:first").focus().addClass("cursor");
}

function change_view_imgs(newval) {
    view_imgs = newval;
    if (view_imgs == 0) {
        $("#actionbar #btn_imgs img").attr('src', '/images/btn_imgs_on.png');
        $("#articles .content_container img").hide();
    } else {
        $("#actionbar #btn_imgs img").attr('src', '/images/btn_imgs_off.png');
        $("#articles .content_container img").show();
    }
}

function toggle_art($hdr){
    var $elm = $hdr.toggleClass("expanded").next();
    $elm.is(":visible") ? $elm.fadeOut("fast") : $elm.fadeIn("fast");
}

function cycle_art_state($img) {
    var st = parseInt($img.attr("alt"));
    if (st>=0 && st<=4) {
        st = st==4 ? 0 : st+1;
        $img.attr({src: '/images/'+imgs_state[st], alt: st});
    }
}

function open_art_link($a){
    // $a.target = "_blank";
    window.open($a.attr('href'));
    art_focus($a.parent().parent().parent().parent());
}

function process_arts() {
    var arts = new Array();
    $("#articles .art:visible .mnhdr1 img.icon").each(function(idx, img) {
        arts[idx] = $(this).attr('name') + ':' + $(this).attr('alt');
    });
    arts = arts.join(',');
    if (!arts)
        return;
    $("#contents").empty().append(div_loading);
    sel = $("#sidebar .selected").find("a").attr('onclick');
    $.post("/ajax/process_articles", {"arts": arts})
        .done(function() {
            sidebar_load(sel);
            show_articles(wis);
        })
        .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR processing articles</div>")
        });
}

function load_arts(num, total, arts) {
    $("#articles .mnhdr .details .num_arts").text(num + " of " + total + " articles");
    if (num < total) {
        $("#articles .mnhdr a.showmore").show();
        $("#articles .mnhdr a.showall").show();
    } else {
        $("#articles .mnhdr a.showmore").hide();
        $("#articles .mnhdr a.showall").hide();
    }
    $arts.append(arts);
    if (num > 0) {
        var $popup_states = $("<div class='popup_states'><ul><li><a name='0'><img src='/images/st_delete.png'/>Delete</a></li><li><a name='1'><img src='/images/st_unread.png'/>Unread</a></li><li><a name='2'><img src='/images/st_starred.png'/>Starred</a></li><li><a name='3'><img src='/images/st_later.png'/>Later</a></li><li><a name='4'><img src='/images/st_archived.png'/>Archived</a></li></ul></div>")
            .popup().appendTo("#articles");
        $popup_states.find('a').click(function() {
            var st = $(this).attr('name');
            $popup_states.data('art').find(".mnhdr1 img.icon").attr({src: '/images/'+imgs_state[st], alt: st});
            $.popup.off($popup_states);
            return false;
        });
        calc_art_titlewrap_width();
        $("#articles .mnhdr1").css("cursor", "pointer").unbind().click(function() { toggle_art($(this)); });
        $("#articles .mnhdr1 img.icon").unbind().mouseenter(function() {
            $.popup.toggle($popup_states, $(this));
            return false;
        });
        $("#articles .mnhdr1 a.title").unbind().click(function() { open_art_link($(this)); return false; });
        $("#articles .art").unbind().click(function() { art_focus($(this)); });
        if ($("#articles .cursor:eq(0)").length == 0)
            $("#articles .art:visible:first").focus().addClass("cursor");
    }
    change_view_imgs(view_imgs);
    change_view(viewtype);
}

function show_articles(l_wis) {
    wis = l_wis;
    offset = DEFAULT_OFFSET;
    limit = DEFAULT_LIMIT;
    $("#contents").empty().append(div_loading);
    $.getJSON("/ajax/articles/" + wis + "/" + sorttype + "/" + offset + "/" + limit)
    .done(function(data) {
        // action bar
        $("#contents").empty().append(build_actionbar());
        $("#actionbar #lbl_show").text(wis2st_str(wis));
        $("#actionbar #popup_show li").click(function() {
            var st = $(this).attr('name');
            show_articles(wis.slice(0, -1)+st);
        });
        $("#actionbar #lbl_filter").text(filter2str(0)); // no filter at start
        $("#actionbar #popup_filter li").click(function() {
            change_filter(parseInt($(this).attr('name')));
        });
        $("#actionbar #lbl_sort").text(sort2str(sorttype));
        $("#actionbar #popup_sort li").click(function() {
            change_sort($(this).attr('name'));
            show_articles(wis);
        });
        $("#actionbar #btn_view").click(function() {
            change_view((viewtype==0) ? 1 : 0);
        })
        $("#actionbar #btn_imgs").click(function() {
            change_view_imgs((view_imgs==0) ? 1 : 0);
        })
        $("#actionbar #popup_mark li").click(function() {
            var st = parseInt($(this).attr('name'));
            if (st>=0 && st<5)
                $("#articles .art:visible .mnhdr1 img.icon").each(function() {
                    $(this).attr({src: '/images/'+imgs_state[st], alt: st});
                });
            else // st==5=> restore state
                show_articles(wis);
        });
        $("#actionbar #btn_process").click(function() {
            process_arts(wis);
        });
        // header
        num_arts = data.num_query;
        $arts = $("<div id='articles'>").appendTo("#contents");
        $arts.append("<div class='mnhdr'>" + data.title + "<span class='details'><span class='num_arts'/><span class='num_hidden'/><a class='showmore'>load more</a><a class='showall'>load all</a></span></div>");
        $("#articles .mnhdr a.showmore").click(function() { load_more_arts(); });
        $("#articles .mnhdr a.showall").click(function() { load_all_arts(); });
        // articles
        load_arts(data.num_query, data.num_total, data.arts);
    })
    .fail(function() {
        $("#contents").empty().append("<div class='error'>ERROR loading articles</div>")
    });
}

function art_focus($art) {
    $("#articles .art").removeClass("cursor");
    $art.focus().addClass("cursor");
    if ($art.position().top + $art.height() > $("#articles").height() || $art.position().top < 0)
        $("#articles").scrollTop($art.get(0).offsetTop);
    if ($art.find(".mnhdr1 img.icon").attr('name') == $("#articles .art:visible:first .mnhdr1 img.icon").attr('name'))
        $("#articles").scrollTop(0);
}

function next_visible_art($art) {
    while (true) {
        if ($art.is(":last-child"))
            return;
        $art = $art.next();
        if ($art.is(":visible"))
            return $art;
    }
}

function prev_visible_art($art) {
    while (true) {
        if ($art.prev().is($("#articles .mnhdr")))
            return;
        $art = $art.prev();
        if ($art.is(":visible"))
            return $art;
    }
}

function load_more_arts() {
    var $dlg = $("").modaldialog2().attr("title", "Loading articles");
    offset += limit;
    $.getJSON("/ajax/articles/" + wis + "/" + sorttype + "/" + offset + "/" + limit)
        .done(function(data) {
            num_arts += data.num_query;
            load_arts(num_arts, data.num_total, data.arts);
            $.modaldialog2.end($dlg);
        })
        .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR loading articles</div>")
        });
}

function load_all_arts() {
    var $dlg = $("").modaldialog2().attr("title", "Loading articles");
    offset = limit = 0;
    $.getJSON("/ajax/articles/" + wis + "/" + sorttype + "/" + offset + "/" + limit)
        .done(function(data) {
	    var num = $(".art").index($(".cursor")); // save cursor position
	    $(".art").remove();
            num_arts = data.num_total;
            load_arts(num_arts, data.num_total, data.arts);
	    art_focus($(".art:eq("+num+")")); // restore cursor position
            $.modaldialog2.end($dlg);
        })
        .fail(function() {
            $("#contents").empty().append("<div class='error'>ERROR loading articles</div>")
        });
}

function handle_arts_keys(ev, $art) {
    var val = false;
    if (ev.ctrlKey)
        return true;
    switch (ev.keyCode || ev.altKey) {
        // global
        case 27: // esc
            sidebar_toggle();
            break;
        case 72: // h
            home();
            break;
        case 70: // f
            summary_group(-1);
            break;
        case 55: // /
            search();
            break;
        case 82: // r
            sidebar_load();
            go(wis);
            break;
        case 85: // u
            goto_unread();
            break;
        case 222: // ? in firefox
        case 191: // ? in google chrome
            help_keys();
            break;
        // movement
        case 74: // j
            var $new = next_visible_art($art);
            if ($new != undefined)
                art_focus($new);
            break;
        case 32: // SPC
            var $last = $new = $art
            while (true) {
            var $new = next_visible_art($new);
                if ($new == undefined || $new.position().top + $new.height() > $("#articles").height())
                    break;
                $last = $new;
            }
            if ($new != undefined)
                art_focus($new);
            else if ($last != undefined)
                art_focus($last);
            break;
        case 75: // k
            var $new = prev_visible_art($art);
            if ($new != undefined)
                art_focus($new);
            break;
        case 8: // BackSpace
            var to = $("#articles").scrollTop() - $("#articles").height();
            var $new = $("#articles .art:visible:first");
            while (true) {
                if ($new == undefined || $new.get(0).offsetTop > to)
                    break;
                $new = next_visible_art($new);
            }
            if ($new != undefined)
                art_focus($new);
            break;
        case 78: // n
            var $new = next_visible_art($art);
            if ($new != undefined) {
                $art.find(".mnhdr1").removeClass("expanded").next().hide();
                $new.find(".mnhdr1").addClass("expanded").next().show();
                art_focus($new);
            }
            break;
        case 80: // p
            var $new = prev_visible_art($art);
            if ($new != undefined) {
                $art.find(".mnhdr1").removeClass("expanded").next().hide();
                $new.find(".mnhdr1").addClass("expanded").next().show();
                art_focus($new);
            }
            break;
        case 36: // home
            art_focus($("#articles .art:visible:first"));
            $("#articles").scrollTop(0);
            break;
        case 35: // end
            art_focus($("#articles .art:visible:last"));
            window.scroll(0, window.scrollMaxY);
            break;
        // scroll
        case 38: // cursorup
            $("#articles").scrollTop($("#articles").scrollTop() - 25);
            break;
        case 40: // cursordown
            $("#articles").scrollTop($("#articles").scrollTop() + 25);
            break;
        case 33: // pageup
            $("#articles").scrollTop($("#articles").scrollTop() - $("#articles").height());
            break
        case 34: // pagedown
            $("#articles").scrollTop($("#articles").scrollTop() + $("#articles").height());
            break
        // change view, toggle images, toggle art view, change state,open, process, load more
        case 49: // 1
            change_view(1);
            break;
        case 50: // 2
            change_view(0);
            break;
        case 73: // i
            change_view_imgs((view_imgs==0) ? 1 : 0);
            break;
        case 13: // enter
        case 86: // v
            toggle_art($art.find(".mnhdr1"));
            art_focus($art);
            break;
        case 83: // s
            cycle_art_state($art.find(".mnhdr1 img.icon"));
            break;
        case 79: // o
            open_art_link($art.find(".mnhdr1 a.title"));
            break;
        case 65: // Shift + a
            if (ev.shiftKey)
                if (confirm('Process articles?'))
                    process_arts();
            break;
        case 77: // Shift + m
            if (ev.shiftKey)
                if ($("#articles .mnhdr a.showmore").is(':visible'))
                    load_more_arts();
            break;
        case 84: // Shift + t
            if (ev.shiftKey)
                if ($("#articles .mnhdr a.showall").is(':visible'))
                    load_all_arts();
            break;
        default:
            val = true;
    }
    return val;
}


//////////////////////////////////////////////////////////////////////////
// Dialogs & messages
var div_loading = "<div class='loading'><div>Loading...</div><br/><img src='/images/loading.gif' /></div>";
var div_updating = "<div class='loading'><div>Updating feeds...</div><br/><img src='/images/loading.gif' /></div>";
var div_processing = "<div class='loading'><div>Processing...</div><br/><img src='/images/loading.gif' /></div>";
var div_importing = "<div class='loading'><div>Importing...</div><br/><img src='/images/loading.gif' /></div>";


//////////////////////////////////////////////////////////////////////////
// My own modal dialog
(function($) {

    // modal dialog for forms
    $.fn.modaldialog = function() {
        var doch = $(document).height(),
        winh = $(window).height(),
        winw = $(window).width();
        var $dialog = $("#dialog").empty();
        var $overlay = $("#overlay")
            .css({'top': 0, 'left': 0, 'height': doch, 'width': winw, 'opacity': 0})
            .show().animate({'opacity': 0.8});
        $(this).appendTo($dialog);
        $("#page").css({"opacity": 0.4});
        // calc size and pos, add and display dialog
        var w = $dialog.width(),
        h = $dialog.height(),
        top = winh/2 - Math.floor(h/2) + 'px',
        left = winw/2 - Math.floor(w/2) + 'px';
        $dialog
            .fadeIn()
            .css('top', top).css('left', left)
            .keydown(function(e) { e.stopPropagation(); })
            .find("input:first").focus();
        $dialog.find("input[name='cancel']").click(function() {
            $dialog.fadeOut();
            $overlay.hide();
            $("#page").css({"opacity": 1});
            return false;
        });
        return $dialog;
    };
    $.modaldialog = $.modaldialog || {};
    $.modaldialog.error = function($obj, msg) {
        $obj.find("div.dlgerr").remove();
        $("<div class='dlgerr'><img src='/images/error.png'/>&nbsp;&nbsp;" + msg + "</div>")
            .insertBefore($obj.find("form table"))
            .effect("highlight", {"color": "#eeeecc"}, 1000);
        $obj.find("input:first").focus();
    };
    $.modaldialog.end = function($obj) {
        $obj.fadeOut();
        $("#overlay").hide();
        $("#page").css({"opacity": 1});
    };

    // modal dialog2
    $.fn.modaldialog2 = function() {
        var doch = $(document).height(),
        winh = $(window).height(),
        winw = $(window).width();
        var $dlg = $("#dlg_loading").empty();
        $("#overlay").css({'top': 0, 'left': 0, 'height': doch, 'width': winw, 'opacity': 0.8}).show();
        $(this).appendTo($dlg);
        $("#page").css({"opacity": 0.4});
        // calc size and pos, add and display dialog
        var w = $dlg.width(),
        h = $dlg.height(),
        top = winh/2 - Math.floor(h/2) + 'px',
        left = winw/2 - Math.floor(w/2) + 'px';
        $dlg.css('top', top).css('left', left).fadeIn().focus()
            .keydown(function(e) { e.stopPropagation(); });
        return $dlg;
    };
    $.modaldialog2 = $.modaldialog2 || {};
    $.modaldialog2.end = function($obj) {
        $obj.fadeOut();
        $("#overlay").hide();
        $("#page").css({"opacity": 1});
    };

    // modal dialog 3: for keybindings
    $.fn.modaldialog3 = function() {
        var doch = $(document).height(),
        winh = $(window).height(),
        winw = $(window).width();
        var $dlg = $("#dlg_help").empty();
        $("#overlay").css({'top': 0, 'left': 0, 'height': doch, 'width': winw, 'opacity': 0.8}).show();
        $(this).appendTo($dlg);
        $("#page").css({"opacity": 0.4});
        // calc size and pos, add and display dialog
        var w = $dlg.width(),
        h = $dlg.height(),
        top = winh/2 - Math.floor(h/2) + 'px',
        left = winw/2 - Math.floor(w/2) + 'px';
        $dlg.css('top', top).css('left', left).fadeIn().focus()
            .keydown(function(e) {
                if (e.keyCode == 27) // esc
                    $.modaldialog3.end($(this));
                e.stopPropagation();
            });
        return $dlg;
    };
    $.modaldialog3 = $.modaldialog3 || {};
    $.modaldialog3.end = function($obj) {
        $obj.fadeOut();
        $("#overlay").hide();
        $("#page").css({"opacity": 1});
    };

    // popup
    $.fn.popup = function() {
        $(this).mouseleave(function () { $.popup.off($(this)); });
        return $(this);
    };
    $.popup = $.popup || {};
    $.popup.toggle = function($dlg, $obj) {
        $dlg.is(':visible') ? $.popup.off($dlg) : $.popup.on($dlg, $obj);
    };
    $.popup.on = function($dlg, $obj) {
        $dlg.data('art', $obj.parent().parent());
        var x = $obj.position().left - 8;
        // FIXME: check x < window width
        var y = $obj.position().top + $obj.outerHeight() + 5;
        if (y+$dlg.outerHeight() > $("#articles").height())
            y = $("#articles").scrollTop() + $("#articles").height() - $dlg.outerHeight() + 8;
        else
            y += $("#articles").scrollTop();
        $dlg.css({left: x, top: y}).fadeIn("fast")
    };
    $.popup.off = function($dlg) {
        $dlg.data('art', null);
        $dlg.fadeOut();
    };

})(jQuery);


//////////////////////////////////////////////////////////////////////////
