<%def name="sign_out_form()">
  <form method="POST" action="${request.make_path('/sign-out')}"
        class="form-inline sign-out-form">
    ${request.csrf_tag}
    <input type="submit" value="Sign Out" class="btn btn-primary">
  </form>
</%def>
