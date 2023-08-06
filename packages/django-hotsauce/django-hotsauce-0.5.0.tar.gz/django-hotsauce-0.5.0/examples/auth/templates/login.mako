## -*- coding: utf-8 -*-

<h2>Sign In</h2>

It Works!




<%def name="login(text='')">

<% 
login_form = data['login_form']
%>

Please log in:

<form action="/session_login/" method="POST">
${login_form}
<input type="submit" value="Send"/>
</form>

% if data['msg']:
<p>${data['msg']}</p>
% endif
</%def>

${login()}
