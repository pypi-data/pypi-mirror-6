## -*- coding: utf-8 -*-
<%page cached="True" />
<%namespace file="layout.mako" import="user_message"/>
<div class="ui-bd-standard fr">
<p class="smalltext ar">
${user_message()}
</p>

## <strong class="email"><a href="mailto:info@gthc.org" class="nounderline">info at gthc.org</a></strong></p>
## TODO: Custom navigation with YAML

<ul class="link-nav fr">
<li><a href="/about/">About</a></li>
<li><a href="/jobs/">Careers</a></li>
##<li><a href="/feeds/">Feeds</a></li>
<li><a href="/contact/"><span>Contact</span></a></li>
<li><a href="http://mercurial.gthc.org/"><span>Repositories</span></a></li>
<li><a href="/wiki/"><span>Wiki</span></a></li>
</ul>
<br/>
<ul class="link-nav-secondary fr">
 ##secondary links
 ##bugzilla.gthc.org
 <li><a href="mailto:bugzilla@gthc.org?Subject=Bug%20Report">Report a bug</a></li>
 <li><a href="/request_a_quote/">Request a quote</a></li>
</ul>
</div>
<br class="clear"/>
##<script type="text/javascript">
##$(function(){
##$('#close-ui-button').bind('click', function(){
##$('ul.link-nav-secondary ui-slide-up').find('a').each(function(){
##$(this).fadeOut();
##});
##});
##});
##</script>
