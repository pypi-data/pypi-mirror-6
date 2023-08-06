## coding: utf-8 
<%inherit file="base.mako" />
<% message = data['message'] %>
<%namespace file="/blogengine/components.mako" import="url_to" />
<% 
obj = data['obj'] 
to = data['to']
sender = data['sender']
%>
<style>
.ui-message {
    background-color: #f2f2f2;
    font-size: 95%;
    margin: 10px;
    padding: 10px;
    border: 1px solid #888;

}
</style>

<div class="ui-message">
<p>
Dear ${to}, ${sender} wants to share an article with you! 
To view this article on line, <a href="https://gthc.org${obj.get_absolute_url()}" title="${obj.title}">click here</a>.
</p>

${sender} also added a personal message:
<br/>
<p>
${message}
</p>
<hr />
<small class="ui-footer">
 The admin team at <a href="https://www.gthc.org/">www.gthc.org</a>. For questions
 about this mail, send inquiries to <a href="mailto:info@gthc.org">info at gthc.org</a>. 
</small>
</div>

