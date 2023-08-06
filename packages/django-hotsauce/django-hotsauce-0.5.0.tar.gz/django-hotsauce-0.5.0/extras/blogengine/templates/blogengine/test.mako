## -*- coding: utf-8 -*-

<%page cached="False" />
<%namespace file="components.mako" import="headline, pager" />

<%
## Get the latest entries and sort them by their
## pub_date in descending order.
entries = data['entries']
##entries.sort(lambda x, y: cmp(x.pub_date, y.pub_date))
##entries.reverse()
entries_count = data['max_items_count']
categories = data['categories']
page_num = data['page_num']
page_mod = data['page_mod']
next_page = data['next_page']
prev_page = data['prev_page']
##settings = data['settings']
##request = data['request']
%>

## synbio = biological exploits (scientist = moo eVi| h4ck3rz)
<%def name="latest_posts(entries, title='News')">
<h2 class="pinkbg">${title}</h2>
%for item in entries:
<h3>
<a href="${item.get_absolute_url()}" title="${item}">${item}</a>
</h3>
%endfor
##${pager()}
## front-end admin panel
##% if request.user:
##<div class="ui-button generic bluebg">
## <span><a href="/blog/posts/add/">Create a new article</a></span>
##</div>
##% endif
</%def>

<div class="colsm fl" id="col1">
 ${latest_posts(entries)}
</div>

<div class="colsm fr" id="col2">
<div class="generic greybg2">
<h2 class="message pinkbg">Categories</h2>
<ul class="colorList">
% for item in categories:
<li><a href="/blog/categories/${item.slug}/">${item.slug} (${item.get_items_count()})</a></li>
% endfor
</ul>
</div>

<div class="generic greybg2">
<h2 class="message pinkbg">Bookmarks</h2>
<ul id="rss-widget" class="colorList">
</ul>

##% if 'DELICIOUS_USERNAME' in settings:
##<%include file="delicious_widget.mako" />
##% endif
</div>
</div>
<br class="clear"/>

<%def name="extra_js()">
<% prefix = data['MEDIA_URL'] %>
##<script src="${prefix}js/tm_api-2.0/src/colorlist.js" type="text/javascript"></script>
<script>
(function($){
## custom accordion navigation (left)
##$('#col1').accordion({
##header: 'h3',
##active: false,
##event: 'mouseover'
##});
$('#rss-widget').getFeed('/feeds/21/', 'li');
$('ul.colorList').eq(0).colorList({class: 'pinkbg'});
})(jQuery);
</script>
</%def>

${extra_js()}
