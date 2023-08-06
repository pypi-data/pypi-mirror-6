## -*- encoding: utf-8 -*-
<%inherit file="/blogengine/base.mako" />
<%page cached="False" />
<%
request = data['request']
user = request.get_remote_user()
form = data['form']
message = data['message']
title = data['title'].encode('utf-8', 'replace')
oid = data['oid']
%>

<%def name="extra_js()">
<%
media_prefix = data['MEDIA_URL']
%>
<script type="text/javascript" src="${media_prefix}js/jquery/jquery.autocomplete.min.js">
</script>
</%def>


<h2>Blog admin: "${title}"</h2>

<div class="ui-editor whitebg generic" id="ui-editor-0">
<form id="editEntryForm" action="." method="POST"> 
<table>
 <tbody>
 ${form.as_table()}
 </tbody>
</table>
 <div class="messagebox pinkbg ar">
  <input id="saveBtn" type="submit" value="Save changes" />
 </div>
</form>
</div>
</div>

${extra_js()}
