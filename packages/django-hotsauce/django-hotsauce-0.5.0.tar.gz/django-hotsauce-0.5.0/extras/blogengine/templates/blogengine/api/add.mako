<%inherit file="/blogengine/base.mako" />
<%
request = data['request']
user = request.remote_user
form = data['form']
message = data['message'] or ''
%>

<%def name="extra_js()" cached="True">
<%
prefix = data['MEDIA_URL']
%>
<script src="${prefix}js/jquery/jquery.autocomplete.min.js"></script>
</%def>


<div class="whitebg generic" id="ui-editor-0">
<h2 class="pinkbg">Create a new article</h2>

% if message != '':
<div class="orangebg ui-message messagebox">${message}</div>
% endif

<form id="addEntryForm" action="/blog/create/" 
 method="POST" enctype="multipart/form-data" class="ui-editor">
<table>
 <tbody>
 ${form.as_table()}
 </tbody>
</table>
 <div class="messagebox pinkbg ar">
  <input id="saveBtn" type="submit" value="Save">
  <input id="addAnotherBtn" type="reset" value="Add another">
 </div>
</form>

##% if form.errors:
##<div class="messagebox error">
##${form.errors}
##</div>
##% endif

</div>

${extra_js()}
