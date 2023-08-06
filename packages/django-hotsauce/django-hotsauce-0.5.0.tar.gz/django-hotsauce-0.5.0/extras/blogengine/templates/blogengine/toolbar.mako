## -*- coding: utf-8 -*-

<div class="generic">
%if b1:
  ## Babel-Django (i18n) stuff
  ## <h4>Articles récents</h4>
  ## <ul>
  ## % for obj in latest_blog_entries:
  ##  <li><a href="${obj.get_absolute_url()}" title="${obj}">${obj.get_absolute_url()}</a></li>
  ## % endfor
  ## </ul>
	<h3>${b1.title}</h3>
  <p>${b1.full_text}</p>
%else:
<p class="error">No latest object here.</p>
%endif

## {% regroup latest|dictsortreversed:"pub_date" by pub_date as grouped %}
## {% for group in grouped %}
## <dl>
##		<dt>{{ group.grouper|date:"N Y" }}</dt>
##		{% for obj in group.list|slice:":5" %}
##				<dd><a href="{{ obj.get_absolute_url }}" title="{{ obj }}">{{ obj }}</a></dd>
##		{% endfor %}
## </dl>
## {% endfor %}


<%doc>
TODO: Arrange categories by a logical order (most recent category?).
{% regroup categories by name as grouped %}
</%doc>

%if categories:
	<h4>Catégories</h4>
	<ul>
	% for obj in categories:
			<li><a href="{{ obj.get_absolute_url }}" title="{{ obj }}" rel="{{ obj }}">{{ obj }}</a> ({{ obj.categories.count }})</li>
	% endfor
	</ul>
%endif
</div>

