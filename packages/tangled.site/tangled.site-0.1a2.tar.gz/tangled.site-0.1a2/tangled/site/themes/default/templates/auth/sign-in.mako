<%inherit file="../base.mako"/>

<%block name="page_title">Sign In</%block>

<%block name="content">
  <form method="post" action="${request.make_path('/sign-in')}">
    ${request.csrf_tag}

    <div class="row">
      <div class="col-xs-4 form-group">
        <input name="username" type="text" class="form-control"
               required="required" autofocus="autofocus"
               placeholder="Username or email address">
        <input name="password" type="password" class="form-control"
               required="required"
               placeholder="Password">
      </div>
    </div>

    <input type="submit" value="Sign In" class="btn btn-default">
    </div>

    ## If the came_from param is present, that indicates that the user
    ## was redirected here when attempting to access a protected page.
    ## Otherwise, the user clicked the "Sign In" link or accessed the
    ## /sign-in page directly.
    <% came_from = request.params.get('came_from') or request.referer or '' %>
    <input type="hidden" name="came_from" value="${came_from}">
  </form>
</%block>
