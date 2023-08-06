## -*- coding: utf-8 -*-
<%inherit file="frontpage.html" />
<% items = data['resultset'] %>

<h3>Categorie: foo</h3>
<ul>
% for item in items:
<li>${item}</li>
% endfor
</ul>

