## coding: utf-8
<%inherit file="base.mako" />
## set this to False to avoid POST issues in saveComment
<%page cached="True" />
<%namespace file="components.mako" import="headline" />
<%namespace file="blogentry_comment_thread.mako" import="comments_for_item" />

<% 
result = data['result'] 
settings = data['settings']
author = data['result'].author
%>

##<%def name="meta()">
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

<div class="colsm fl" id="col1">
##<p>Author: <a href="/blog/authors/${author}/" title="Article written by ${author}.">${author}</a></p>

<div class="generic greybg2" id="top">
${headline(result, nolinks=True, fulltext=True)}
<hr/>
## API actions for editors 
<div class="messagebox whitebg ui-menu">
<ul class="colorList">
<li>
<span><a href="/blog/posts/delete/${result.s.oid}/">Delete this article</a></span>
</li>
<li>
<span><a href="/blog/posts/edit/${result.s.oid}/">Edit</a></span>
</li>
<li>
<span><a href="/blog/posts/send-to-friend/${result.s.oid}/">Tell a friend</a></span>
</li>
<li>
<span>
<a href="/blog/posts/subscribe/${result.s.oid}/">Subscribe to the RSS feed
</a>
</span>
</li>
<li>
<span><a href="#top">Back to the top</a></span>
</li>
</ul>
</div>

</div>
</div>

## Comments 
<div class="colsm fr" id="col2">
 <div class="generic greybg2">
 ${comments_for_item()}
 </div>
</div>

<script type="text/javascript">
$(function(){
$('.colorList').eq(0).colorList({class:'pinkbg'});
});
</script>
