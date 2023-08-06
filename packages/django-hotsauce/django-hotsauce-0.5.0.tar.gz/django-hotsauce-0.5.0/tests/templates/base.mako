## -*- coding: utf-8 -*-
<% 
media_prefix = data['MEDIA_URL'] 
%>
<%page cached="False" />

## quotes.yaml:
## Breaking from uniformity since 2007
<%def name="title(text)">
Green Tea Hackers Club HQ || ${text}
</%def>

<%def name="required_js(prefix)">
<% jquery_prefix =  prefix + "js/jquery-ui-1.7.3-custom/js/" %>
<script src="${prefix}js/jquery/jquery-1.3.2.min.js"></script>
## jquery tools (scrollable)
##<script src="${prefix}js/jquery-tools/jquery.tools.min.js" 
## type="text/javascript"></script>
##<script type="text/javascript">
##jQuery.noConflict();
##</script>
<script src="${jquery_prefix}jquery-ui-1.7.3.custom.min.js"></script>
##<script src="${prefix}js/jquery/jquery.equalheights.js"></script>
##<script src="${prefix}js/jquery/jquery.validate.min.js"></script>
<script src="${prefix}js/jquery/jquery.autocomplete.min.js"></script>
<script src="${prefix}js/jquery/jquery.cycle.min.js"></script>
<script src="${prefix}js/tm_api-2.0/src/core.js"></script>
<script src="${prefix}js/tm_api-2.0/src/ajax-settings.js"></script>
<script src="${prefix}js/tm_api-2.0/src/tabs.js"></script>
<script src="${prefix}js/tm_api-2.0/src/bootstrap-debug.js"></script>
<script src="${prefix}js/tm_api-2.0/src/colorlist.min.js"></script>
<script src="${prefix}js/tm_api-2.0/src/syndication.min.js"></script>
<script src="${prefix}js/tm_api-2.0/src/formvalidator.min.js"></script>
<script type="text/javascript">
$(function(){
$.fn.doInitMain({
colorListClass: 'bluebg',
loaderImageUrl: "${prefix}img/loading.gif"
##tooltipClass: 'tooltip',
##dialogClass: 'ui-dialog'
});
//add navigation breadcrumbs
$('#ui-breadcrump').updateBreadcrump(window.location);

$('#ui-loader').bind('click', function(){
$(this).parents('#ui-breadcrump').fadeOut('fast');
});

//make all .stacked elements the same height
$('#footer').find('span.stacked').each(function(){
$(this).css('height', '250px')
});    
});
</script>
</%def>

<%def name="extra_js()"></%def>

##<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
## "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html lang="en" xml:lang="en">
<head>
<title>
 ${self.title('Open Source Development, Research, Python, Django, Montreal (Quebec)')}
</title>

<%def name="meta()">
<meta charset="UTF-8" />
##<meta http-equiv="Content-Style-Type" content="text/css" />
##<meta http-equiv="Content-Language" content="en" />
<meta name="Author" content="Etienne Robillard" />
<meta name="Keywords" content="gthc,notmm,gthc.org,greenteahackersclub,green tea hackers club" />
<meta name="Description" content="Do what you love, love what you do." />
## SEO stuff:
## <meta name="Copyright" content="Copyright (c) 2010, Etienne Robillard. All rights reserved" />
##<meta name="alexaVerifyID" content="UVOGmg4KAMthOcaroyO9YJr-1t4" />
## Google stuff (optional)
## <meta name="google-site-verification" content="k1TgSERYd18-qSmj_NUMXMWNNVMv3TgG1CWWTncp464" />
</%def>

<%def name="extra_css(media_prefix)" cached="False">
<link href="${media_prefix}favicon.ico" rel="SHORTCUT ICON" />
<link href="${media_prefix}css/reset.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/layout.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-colorlist.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-style.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-tabs.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-base.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-forms.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-slideshow.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-css3.css" type="text/css" rel="stylesheet" />
<link href="${media_prefix}css/ui-tablesorter.css" type="text/css" rel="stylesheet"/>
<link href="${media_prefix}css/ui-autocomplete.css" type="text/css" rel="stylesheet" />
<!--[if lte IE 7]>
<link href="${media_prefix}css/jquery.tabs-ie.css" type="text/css" rel="stylesheet" />
<![endif]-->
<link href="${media_prefix}js/jquery-ui-1.7.3-custom/css/smoothness/jquery-ui-1.7.3.custom.css"
type="text/css" rel="stylesheet" media="all" />
</%def>

${self.required_js(media_prefix)}
${self.extra_css(media_prefix)}
${self.meta()}
${self.extra_js()}
</head>
<body>
${next.body()}
##<br class="clear" />
##<div id="rightCol" class="col100">
##<%include file="/widgets/gala-draconica.html" />
##<div style="font-size: 9.5px; padding-left: 30px">Advertisement</div>
##</div>
</body>
</html>
## EOF
