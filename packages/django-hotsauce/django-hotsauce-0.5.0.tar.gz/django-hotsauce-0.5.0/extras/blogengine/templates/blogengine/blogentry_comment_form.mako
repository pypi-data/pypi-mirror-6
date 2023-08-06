## coding: utf-8
<% 
##media_prefix = data['MEDIA_URL'] 
##settings = data['request'].session.settings
comment_form = data['comment_form']
%>

<div id="ui-comment-form" class="greybg generic b1">
##<span class="ui-slide-down">Add new comment</span>
##<span class="ui-slide-up">Close</span>
<form action="." method="post">
<table> 
${comment_form.as_table()}
</table>
</form>
</div>

##${self.extra_css(media_prefix)}
