<%inherit file="base.mako" />

<%block name="page_title">Users</%block>

<%block name="content">
  % for user in users:
    <ul>
      <li>Username: ${user.username or '[username not set]'}</li>
      <li>Email address: ${user.email}</li>
      <li>
        Roles
        <ul>
            % for r in user.roles:
              <li>${r.key} = ${r.description or '[no description]'}</li>
            % endfor
        </ul>
      </li>
      <li>
        Permissions
        <ul>
          % for p in user.permissions:
            <li>${p.key} = ${p.description or '[no description]'}</li>
          % endfor
        </ul>
      </li>
    </ul>
    <form method="post" action="${request.make_path('/user/{}'.format(user.id))}">
      ${request.csrf_tag}
      <input name="$method" type="hidden" value="DELETE" />
      <input type="submit" value="Delete User" />
    </form>
  % endfor
</%block>
