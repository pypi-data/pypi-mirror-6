<%inherit file="../base.mako"/>

<%block name="page_title">Sign Up</%block>

<%block name="content">
  <form method="post" action="${request.make_path('/sign-up')}">
    ${request.csrf_tag}

    <div class="row">
      <div class="col-xs-4 form-group">
        <input type="text" name="username" class="form-control"
               autofocus="autofocus" placeholder="Username (optional)">
        <input type="email" name="email" class="form-control"
               required="required" placeholder="Email Address">
        <input type="password" name="password" class="form-control"
               required="required" placeholder="Password">
      </div>
    </div>

    <input type="submit" value="Sign Up" class="btn btn-default">
  </form>
</%block>
