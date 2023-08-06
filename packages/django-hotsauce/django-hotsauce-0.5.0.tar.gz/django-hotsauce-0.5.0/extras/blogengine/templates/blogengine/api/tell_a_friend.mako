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
obj = data['obj']
%>

<%def name="extra_js()">
<%
media_prefix = data['MEDIA_URL']
%>
<style type="text/css">
@import "${media_prefix}css/autocomplete.css";
</style>
<script src="${media_prefix}js/jquery/jquery.validate.min.js">
</script>
##<script src="${media_prefix}js/jquery/jquery.autocomplete.min.js">
##</script>
<script type="text/javascript">
$(function(){
$('#SendToFriendForm').validate({
rules: {
 recipient1: 'required',
 subject: 'required',
 message: 'required',
 name: 'required'
}
});
});
</script>
</%def>


<div class="colsm generic greybg2" id="col1">

<h2 class="pinkbg messagebox">Tell a friend: ${obj.title}</h2>

<div class="ui-editor whitebg generic" id="ui-editor-0">
% if message != '':
<div class="orangebg ui-message messagebox">${message}</div>
% endif

<form id="SendToFriendForm" action="/blog/posts/send-to-friend/${oid}/"
      method="post" class="ui-form"> 
<table>
 <tbody>
 ${form.as_table()}
 </tbody>
</table>
 <div class="ui-menu ar">
  <input id="sendBtn" type="submit" value="Send!">
 </div>
</form>
</div>
</div>

${extra_js()}
