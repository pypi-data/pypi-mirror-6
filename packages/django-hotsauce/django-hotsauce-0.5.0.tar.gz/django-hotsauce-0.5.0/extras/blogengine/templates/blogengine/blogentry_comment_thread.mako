## -*- coding: utf-8 -*-
<%inherit file="base.mako" />

<%def name="comments_for_item()">
<%
result = data['result'] 
media_prefix = data['MEDIA_URL']
comments = data['comments']
comment_count = len(comments)
u_comment_count = data['u_comments_count']
comments.sort(lambda x, y: cmp(x.pub_date, y.pub_date))
##settings = data['request'].session.settings
##comments.reverse()
%>

<div id="commentPanel" class="ui-comment-thread">
<h2 class="bluebg3">Recent Comments (${comment_count})</h2>
% if comments:

##(${u_comment_count} comment waiting in line)
% for comment in comments:
<% comment_id = comment.s.oid %>
<div class="ui-comment-hd" id="#comment${comment_id}">
<a href="#comment${comment_id}">${comment.sender_name} posted a reply on ${comment.pub_date.strftime("%Y-%m-%d")}</a>
</div>
<div class="ui-comment">
##<a href="#" title="View comment">View comment</a>
<div class="ui-comment-bd">
 ${comment.convert_to_html()}
## <%include file="blogentry_comment_footer.mako" />
</div>
</div>
% endfor
<br/>
% else:
No comments yet!
% endif
</div>

<%include file="blogentry_comment_form.mako" />

<script src="${media_prefix}js/tm_api-2.0/src/comment.js"></script>
<script>
var j = jQuery.noConflict();
(function(j){
    // emulates color lists..
    j('#commentPanel').find('.ui-comment-hd:odd').each(function(){
         j(this).css('background-color', '#fceccc');
         j(this).css('border-bottom', '1px solid #fc8222');
         j(this).css('border-top', '1px solid #fc8222');
         var w = j(this).next('.ui-comment-bd').eq(0).width();
         j(this).css('width', w);
    });
    // toggle on comment visibility
    j('.ui-comment-hd').bind('click', function(){
            j(this).next('.ui-comment').slideToggle().toggleClass('ui-slide-up');
            return false;
    });
    j('.ui-comment').each(function(){j(this).slideToggle('ui-slide up');});

//show the ajax-enabled comment form 
j.get('comment/', function(data){ return j('#'+'ui-comment-form').replaceWith(data); });
})(jQuery); 
</script>
</%def>
##${headline(result, nolinks=True)}
