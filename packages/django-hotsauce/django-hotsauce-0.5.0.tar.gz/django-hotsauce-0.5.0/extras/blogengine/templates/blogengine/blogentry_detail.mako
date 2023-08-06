## coding: utf-8
##<%inherit file="/layout_clean.mako" />
<%inherit file="/layout.mako"/>

## set this to False to avoid POST issues in saveComment
<%page cached="False" />

<%namespace file="components.mako" import="headline" />

##<%namespace file="blogentry_comment_thread.mako" import="comments_for_item" />


<%def name="pagetitle(text='foo')" cached="False">
<% result = data['result'] %>
${result}
</%def>

##<%def name="pagemeta()">
##<%
##result = data['result']
##tagstr = ''.join(["%s," % item.name for item in result.m.tags()])
##tagstr = tagstr.rstrip(',')
##%>
## <link rel="alternate" type="text/rss" ...>
## <meta name="author" content="${result.author}" />
## <meta name="description" content="${result.short_description}" />
##<meta name="keywords" content="${tagstr}" />
##</%def>

<%def name="pagecontent()">
<% 
result = data['result'] 
##addthis_widget = data.get('addthis_widget', 'addthis widget is disabled')
comment_form = data['comment_form']
media_prefix = data['MEDIA_URL']
comments = data['comments']
comment_count = len(comments)
%>
<div class="fl col450">
<div class="fl ui-rounded b1 whitebg">
${headline(result, fulltext=True)}
</div>
<br class="clear"/>

<div class="ui-rounded b1 whitebg">
<h2 class="bluebg3">Add comment</h2>
<form id="commentForm" action="comment/new/" method="POST">
 <table>
 ${comment_form.as_table()}
 </table>
 <p class="ar">
  <input type="button" value="Save" id="commentBtn">
  <input type="hidden" value="${result.get_absolute_url()}" name="id_path">
  <input type="hidden" value="${result._oid}" name="id_oid">
 </p>
</form>
</div>
</div>
## comments div
<div class="fr col250">
<div class="ui-rounded b1 whitebg">
<h2 class="pinkbg">Comments (${comment_count})</h2>
<ul class="colorList greybg2">
% for comment in comments:
<li>

${comment.sender_name}: ${comment.sender_message|h}

</li>
% endfor
</ul>
</div>

</div>

<br class="clear"/>

<script type="text/javascript"
src="${media_prefix}js/tm_api-2.0/src/formvalidator.js">
</script>
<script type="text/javascript">
(function(j){
##Handle the "create account" event and create the
##new user account
##j('#createUserBtn').bind('click', function(){
##alert('Account creation not yet available. Please try again later.');
##});

j('#commentBtn').bind('click', function(){

j('#commentForm').saveForm({
 href: "comment/new/",
 callback: function(data, msg){
    alert(data.result);
 }
 });
});

})(jQuery);
</script>

## script for comments (ajax)
##<script type="text/javascript" src="${media_prefix}js/tm_api-2.0/src/formvalidator.js">
##</script>
##<script>
##(function(j){
##  j('#commentBtn').bind('click', function(){
##   j('#commentform').saveForm({
##        href: "comment/new/",
##        callback: function(data, msg){
##            //buggy or insane jquery ui dialog
##            //j(this).SimpleDialog('Your comment has been saved!', 'Thank you');
##        },     
##    }); 
##   });
##})(jQuery);
##</script>

</%def>
${self.pagecontent()}
