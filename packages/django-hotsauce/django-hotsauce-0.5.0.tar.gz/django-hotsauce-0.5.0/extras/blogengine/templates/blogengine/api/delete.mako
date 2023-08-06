## coding: utf-8 
<%inherit file="/blogengine/base.mako" />
<%
request = data['request']
user = request.remote_user
form = data['form']
message = data['message'] or ''
instance = data['instance']
oid = 111 #data['oid']
%>

<%def name="extra_js()">
<%
media_prefix = data['MEDIA_URL']
%>
<style type="text/css">
@import "${media_prefix}css/autocomplete.css";
</style>
<script src="${media_prefix}js/jquery/jquery.autocomplete.min.js" type="text/javascript">
</script>

</%def>


<div class="colsm generic greybg2" id="col1">

<div class="ui-editor whitebg generic" id="ui-editor-0">

% if message != '':
<div class="orangebg ui-message messagebox">${message}</div>
% endif
<fieldset>
<legend>Entry: ${instance}</legend>
<form id="addEntryForm" action="/blog/posts/delete/${oid}/" method="POST" enctype="multipart/form-data">
<table>
 <tbody>
 ##${form.as_table()}
 ${form}
 </tbody>
</table>
</fieldset>
<fieldset>
<legend>Save changes</legend>
  <div class="ui-button ar">
  <input id="confirmBtn" type="submit" value="Continue!" />
  </div>
</form>
</fieldset>
##% if form.errors:
##<div class="messagebox error">
##${form.errors}
##</div>
##% endif


</div>

</div>

${extra_js()}
