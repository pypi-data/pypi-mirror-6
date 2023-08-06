## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%
## Get the latest entries and sort them by their
## pub_date in descending order.
categories = data['categories']
categories.sort()
%>

<div id="col1" class="colmed">
<div class="ui-widget whitebg b1">
<h2 class="bluebg3">Categories</h2>
<ul class="colorList bluebg">
% for item in categories:
% if item.slug:
<li><a href="/blog/categories/${item.slug}/" title="${item}">${item.slug}</a></li>
% endif
% endfor
</ul>
</div>
</div>

