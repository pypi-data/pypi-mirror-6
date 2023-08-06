## this div will be dynamically updated using ajax
## showing the most 3 recents messages in the "queue".
## by default, the container element (messageList) will
## have prepopulated messages if the user have already posted
## messages
<%inherit file="/blogengine/base.mako" />

<% message_set = data['message_set'] %>
<div id="messageList" class="ui-widget generic greybg2 colsm">
% if message_set:
<ul class="colorList">
% for message in message_set:
    <li>
        <a href="${message.get_absolute_url()}">
            ${message.pub_date.strftime("%Y-%m-%d %H:%m")}:
            ##${message['author']}:
            ${message.content}
        </a>    
    </li>
% endfor
</ul>
% else:
<p>What are you doing?</p>
% endif
</div>
