<%inherit file="base.mako"/>

<%block name="page_title">${settings['site.entries.title']}</%block>

<%block name="content">
  <% non_page_entries = [entry for entry in entries if entry.published and not entry.is_page] %>
  % if non_page_entries:
    % for entry in non_page_entries:
      <h3><a href="/${entry.slug}">${entry.title}</a></h3>
      <p><small>Published ${request.helpers.format_datetime(entry.published_at) or 'Unpublished'}</small></p>
      <div>${entry.content_html | n}</div>
    % endfor
  % else:
    Nothing found
  % endif
</%block>

<%block name="bottom_nav">
  % if request.user:
    <div class="navbar">
      <ul class="nav navbar-nav">
        % if request.user.has_permission('new_entry'):
          <li><a href="${request.resource_url('new_entry')}">New Entry</a></li>
        % endif
      </ul>
    </div>
  % endif
</%block>
