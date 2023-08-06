<%inherit file="base.mako" />

<%block name="page_title">Meta</%block>

<%block name="content">
  <table>
    <tbody>
      % for k, v in sorted(settings.items()):
        <tr style="background-color: #${loop.cycle('fff', 'ddd')};">
          <td>${k}</td>
          <td>${v}</td>
        </tr>
      % endfor
    </tbody>
  </table>
</%block>
