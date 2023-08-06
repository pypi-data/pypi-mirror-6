## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%
media_prefix = data['MEDIA_URL']
##link_set = data['link_set']
%>
<%namespace file="/modules/colorlist.mako" import="colorlist" />

<%def name="header(media_prefix)">
<%include file="tophead.mako" />
##${user_message()}

<%include file="menubar.mako" />
<div id="header" class="whitebg">
<a href="/">
<img src="${media_prefix}img/g3097.png" alt="" />
</a>


</div>
</%def>

<%def name="user_message()">
<%
request = data['request']
user = request.get_remote_user() 
%>

## check for request.user.is_authenticated()
% if user:
<span>Greetings, ${user}. <a href="/session_logout/">[Sign out]</a></span>
% else:
<span>Welcome! Please <a href="/session_login/">login</a> to open a new session.</span>
% endif
</%def>

<%def name="page()" cached="False">
<div id="page">
<br/>
${next.body()}
<br class="clear"/>
</div>
</%def>

<%def name="pageheader()" cached="False">
<div class="pageHeader" id="messagePanel">
<div id="ui-breadcrump">
You are here:
<span class="first">/</span>
<span class="slide-down fr" id="ui-loader">Hide</span>
</div></div>
</%def>

<%def name="footer()" cached="False">
hello
</%def>

## main canvas area
<%def name="content()" cached="True">
<div id="content" class="box-shadow">
 ${self.header(media_prefix)}
 ${pageheader()}
 ${next.page()}
 ##<br class="clear"/>
 ${self.footer()}
</div>
</%def>

${content()}


