<!DOCTYPE html>
<%namespace file="auth/sign-out-form.mako" import="sign_out_form" />
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="shortcut icon" href="${request.make_url('favicon.ico')}" />

    <title>${settings['site.title']}</title>

    <link rel="stylesheet" type="text/css"
          href="${request.static_path('/static/bootstrap/dist/css/bootstrap.min.css')}" />

    <link rel="stylesheet" type="text/css"
          href="${request.static_path('/static/css/base.css')}" />
  </head>

  <body>
    <header>
      <div class="container">
        <div id="meta" class="pull-right">
          <ul class="nav nav-pills">
            % if not user:
              <li><a href="${request.make_path('/sign-up')}">Sign Up</a></li>
              <li><a href="${request.make_path('/sign-in')}">Sign In</a></li>
            % else:
              <li class="dropdown">
                <a href="${request.resource_url('profile')}"
                   class="dropdown-toggle" data-toggle="dropdown">
                  ${user.name or user.username or user.email}
                  <span class="caret"></span>
                </a>

                <ul class="dropdown-menu">
                  <li class="menuitem">
                    <a href="${request.resource_url('profile')}">
                      My Profile
                    </a>
                  </li>

                  % if user.has_role('admin'):
                    <li class="menuitem">
                      <a href="${request.resource_url('admin')}">Admin</a>
                    </li>
                  % endif

                  <li class="divider"></li>

                  <li class="menuitem">${sign_out_form()}</li>
                </ul>
              </li>
            </ul>
          % endif
        </div>
      </div>

      <div class="container">
        <div id="header">
          <%block name="header">
            <a href="/">
              <h1 class="title">${settings['site.title']}</h1>
              <div class="tagline">${settings['site.tagline']}&nbsp;</div>
            </a>
          </%block>
        </div>
      </div>

      <nav role="navigation">
        <div class="container">
          <ul class="nav navbar-nav">
              % if user and user.has_role('admin'):
                <li><a href="${request.resource_url('admin')}">Admin</a></li>
              % endif
            <li><a href="/">Home</a></li>
            <li><a href="${settings['site.entries.path']}">${settings['site.entries.title']}</a></li>
            % for page in pages:
              % if page.slug != settings['site.home']:
                <li><a href="/${page.slug}">${page.title}</a></li>
              % endif
            % endfor
          </ul>
        </div>
      </nav>
    </header>

    <div class="container">
      <h2 id="page-title">
        <%block name="page_title">Page Title Goes Here</%block>
      </h2>
    </div>

    <div class="container">
      <%block name="flash">
        <% flash_messages = request.flash.pop('error') %>
        % if flash_messages:
          <ul class="flash">
            % for message in flash_messages:
              <li class="alert alert-danger">${message}</li>
            % endfor
          </ul>
        % endif

        <% flash_messages = request.flash.pop() %>
        % if flash_messages:
          <ul class="flash">
            % for message in flash_messages:
              <li class="alert alert-success">${message}</li>
            % endfor
          </ul>
        % endif
      </%block>
    </div>

    <div class="container">
      <%block name="content">
        Content goes here
      </%block>
    </div>

    <div class="container">
      <div class="bottom-nav">
        <%block name="bottom_nav"></%block>
      </div>
    </div>

    <footer>
      <div class="container">
        <%block name="footer">
          % if settings.get('site.copyright'):
            <div id="copyright">
              &copy; ${settings['site.copyright'] | n}
            </div>
          % endif
          <div id="powered-by">
            Powered by <a href="http://tangledwebframework.org/">tangled.web</a>
          </div>
        </%block>
      </div>
    </footer>

    <%block name="javascripts">
      <script src="${request.static_path('/static/jquery/jquery.min.js')}"></script>
      <script src="${request.static_path('/static/bootstrap/dist/js/bootstrap.min.js')}"></script>
      <!-- JavaScript tags go here -->
    </%block>
  </body>
</html>
