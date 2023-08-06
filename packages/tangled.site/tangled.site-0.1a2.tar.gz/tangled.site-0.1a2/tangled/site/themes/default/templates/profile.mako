<%inherit file="base.mako"/>

<%block name="page_title">Your Profile</%block>

<%def name="put_form(legend=None, submit_value=None)">
  <% form_action = request.resource_url('user', {'id': user.id}) %>
  <form method="post" action="${form_action}" class="row">
    ${request.csrf_tag}
    <input type="hidden" name="$method" value="PUT">

    <fieldset class="col-xs-4">
      % if legend:
        <legend>${legend}</legend>
      % endif

      <div class="form-group">
        ${caller.body()}
      </div>

      <input type="submit" value="${submit_value or 'Update'}" class="btn btn-default">
    </fieldset>
  </form>
  <br />
</%def>

<%block name="content">
  <%self:put_form legend="Name">
    <input type="text" name="user.name" value="${user.name or ''}" class="form-control">
  </%self:put_form>

  <%self:put_form legend="Username">
    <input type="text" name="user.username" value="${user.username or ''}" class="form-control">
  </%self:put_form>

  <%self:put_form legend="Email Address">
    <input type="text" name="user.email" value="${user.email}" class="form-control">
  </%self:put_form>

  <%self:put_form legend="Change Password" submit_value="Change Password">
    <input type="password" id="user.current_password" name="user.current_password"
           placeholder="Current Password"
           class="form-control">

    <input type="password" id="user.password" name="user.password"
           placeholder="New Password"
           class="form-control">

    <input type="password" id="user.confirm_password" name="user.confirm_password"
           placeholder="Confirm New Password"
           class="form-control">
  </%self:put_form>
</%block>
