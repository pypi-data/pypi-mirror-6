#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.utils.urlmap import RegexURLMap, url

render_to_response = 'blogengine.template.direct_to_template'

urlpatterns = RegexURLMap()

urlpatterns.add_routes('',
   # Frontdoor (a simple generic view)
   url(r'^$|index.html$', render_to_response, {
        'template_name': 'default.mako',
   }),
   url(r'^session_login/$', 'views.login.login')
   )

urlpatterns.commit()
