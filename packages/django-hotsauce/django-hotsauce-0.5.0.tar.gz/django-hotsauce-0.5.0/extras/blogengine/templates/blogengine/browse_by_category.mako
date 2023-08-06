## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>
<%page cached="False" />
<% 
category = data['instance']
related_items = data['related_items']
%>

<div class="colsm whitebg b1 rounded">

<div class="ui-widget generic">
<h2 class="bluebg3">${category.name}</h2>
##<p>${category.description}</p>

% if len(related_items) < 1:
<p class="messagebox pinkbg">There's no posts for this category at the
moment.</p>
% else:
<ul class="colorList">
% for entry in related_items:
% if entry.reviewed:
<li><a href="${entry.get_absolute_url()}">${entry.pub_date}, ${entry.title}</a></li>
% endif
% endfor
</ul>
% endif
</div>

<div class="ui-footer">
 <a href="/blog/categories/">View all categories.</a>
</div>

</div>
