<%inherit file="base.mako"/>

<%block name="page_title">${entry.title}</%block>

<%block name="content">
  <p>
    <small>
      % if request.user and request.user.has_role('admin'):
        Created: ${request.helpers.format_datetime(entry.created_at)}<br/>
        Updated: ${request.helpers.format_datetime(entry.updated_at)}<br/>
      % endif
      Published: ${request.helpers.format_datetime(entry.published_at) or 'Unpublished'}<br/>
    </small>
  </p>
  <div>${entry.content_html | n}</div>
</%block>

<%block name="bottom_nav">
  % if request.user:
    <div class="navbar">
      <ul class="nav navbar-nav">
        % if request.user.has_permission('edit_entry'):
          <li>
            <a href="${request.resource_url('edit_entry', {'id': entry.id})}">Edit</a>
          </li>
        % endif
      </ul>
      % if request.user.has_permission('delete_entry'):
        <form method="POST" action="${request.resource_url('entry', {'id': entry.id})}"
              class="navbar-form navbar-left">
          ${request.csrf_tag}
          <input type="hidden" name="$method" value="DELETE">
          <input type="submit" value="Delete" class="btn btn-danger">
        </form>
      % endif
    </div>
  % endif
</%block>
