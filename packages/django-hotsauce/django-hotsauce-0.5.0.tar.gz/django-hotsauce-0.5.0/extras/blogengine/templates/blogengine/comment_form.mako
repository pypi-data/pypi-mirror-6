## coding: utf-8
<% 
media_prefix = data['MEDIA_URL']
form = data['form']
#hash = data['hash']
%>

<form id="commentform" action="comment/" method="post" 
 enctype="application/x-www-form-urlencoded" class="ui-comment-form">
<div class="commentFormSub">
 <table cellpadding="4" cellspacing="0" width="100%">
 ${form}
 </table>	
</div>
<br />
<div class="ar">
 <input type="button" id="formControlBtn" value="Save" />
 <input type="button" id="commentSlideUpBtn" class="ui-slide-up" value="Close" />
 <input type="reset" id="formControlReset" value="Add another" />
 ##<input id="hash" name="hash" type="hidden" value="${hash}">
</div>
</form>

<script type="text/javascript">
$(function(){
##$('#'+'formControlReset').bind('click', function(){
##$('#'+'commentform').empty()
##});
$('#'+'formControlBtn').bind('click', function(){
$('#'+'commentform').validate();
});

$('#commentSlideUpBtn').bind('click', function(){
$('.commentFormSub').eq(0).slideToggle('fast');
val = $(this).attr('value');
if (val != 'Open') { $(this).attr('value', 'Open') }
else { $(this).attr('value', 'Close') };
});

$('#'+'commentform').find('tr:even').each(function(){
$(this).css('background-color', '#e3b7b7');
});
return false;
});
   
</script>
