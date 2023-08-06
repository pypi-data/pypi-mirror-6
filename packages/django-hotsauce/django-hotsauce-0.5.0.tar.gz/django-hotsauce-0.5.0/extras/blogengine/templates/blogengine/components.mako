##<%inherit file="base.mako" />
## <%page cached="True" />
<% 
result = data['result'] 
media_prefix = data['MEDIA_URL']
%>

<%def name="pager()">
<%
next_page = data['next_page']
prev_page = data['prev_page']
%>
<div class="ui-footer whitebg b1 generic">
<span class="prev fl">
<a href="/blog/?page=${prev_page}">Previous page</a>
</span>
<span class="next fr">
<a href="/blog/?page=${next_page}">Next page</a>
</span>
<br class="clear"/>
</div>
</%def>

<%def name="url_to(item, title='Permalink')">
<% 
t = item.title.decode('utf-8', errors='ignore') 
%>
<a href="${item.get_absolute_url()}" title="${t}">${t}</a>
</%def>

<%def name="headline(item, nolinks=False, fulltext=False, elem='h3')" cached="False">
<%
media_prefix = data['MEDIA_URL']
%>
<h2 class="bluebg3">
 ${item.title}
</h2>

<div class="fr">
% if item.image1:
<img src="${media_prefix}${item.image1}" alt="" width="200px">
% endif
</div>



##<hr/>
## <div class="fl col300 j">
% if fulltext:
 <div class="ui-blogentry">
 ${item.convert_to_html(name='body')}
 </div>
% endif
## </div>
<div class="ui-generic greybg2 fr box-shadow" 
style="font-size: 10px; min-height: 40px; max-width: 80px; padding: 2px">
 Last modified: ${item.pub_date}
</div>
<br class="clear"/>
</%def>

