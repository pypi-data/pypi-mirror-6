<%inherit file="base.mako" />

<%block name="page_title">Admin</%block>

<%block name="content">
  <ul>
    % for resource in resources:
      <% name = resource.name %>
      <li><a href="${request.resource_path(name)}">${name.split('admin/', 1)[1]}</a></li>
    % endfor
  </ul>
</%block>
