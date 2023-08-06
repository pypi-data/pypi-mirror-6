## -*- coding: utf-8 -*-
<%def name="colorlist(title, items)">
<h2 class="message pinkbg">${title}</h2>
##TODO: add random link list rotations (categories of links=(freesoft.yaml, webappsec.yaml) 
<ul class="colorList">
%for item in items:
 <li><a href="${item['href']}" title="${item['title']}">${item['title']}</a></li>
%endfor
</ul>
</%def>

<%def name="simplelist(title, items)">
<h3>${title}</h3>
%for item in items:
<a href="${item['href']}" title="${item['title']}">${item['title']}</a>
%endfor
</%def>
