## -*- coding: utf-8 -*-
## a flexible contact/comment form

<%def name="contact_form(form, media_prefix, hash)">
<div class="fl">
<h4>Boîte aux lettres</h4>
</div>

<div class="fr">
##<img alt="email icon" src="${media_prefix}img/icons/icon_email.gif" />
<img src="${media_prefix}img/email.png" alt="email icon" />
</div>
<br class="clear" />
<form id="contactform" action="/" method="post">
<table cellpadding="0" cellspacing="0">
	${form}
</table>	
<div class="ar">
    <input id="cfbtn" type="button" value="OK" />
    <input id="cfreset" type="reset" value="Reset" />
    ## <input id="hash" name="hash" type="hidden" value="${hash}" />
</div>
</form>
<p id="cfresult"></p>
</%def>

