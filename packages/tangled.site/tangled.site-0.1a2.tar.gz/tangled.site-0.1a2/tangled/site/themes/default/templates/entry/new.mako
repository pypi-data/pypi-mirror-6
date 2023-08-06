<%inherit file="base.mako"/>

<%block name="page_title">New Entry</%block>

<%block name="content">
  <form method="POST" action="${request.make_path('/entries')}">
    ${request.csrf_tag}

    <fieldset>
      <div class="checkbox">
        <label for="entry.published">Published?</label>
        <input type="checkbox" id="entry.published" name="published"
               ${'checked="checked"' if entry.published else ''}>
      </div>

      <div class="checkbox">
        <label for="entry.is_page">Page?</label>
        <input type="checkbox" id="entry.is_page" name="is_page"
               ${'checked="checked"' if entry.is_page else ''}>
      </div>

      <div class="row">
        <div class="form-group col-xs-2">
          <label for="entry.slug">Slug</label>
          <input type="text" id="entry.slug" name="slug" size="30" class="form-control">
        </div>
      </div>

      <div class="row">
        <div class="form-group col-xs-4">
          <label for="entry.title">Title</label>
          <input type="text" id="entry.title" name="title" size="30" class="form-control">
        </div>
      </div>

      <div class="row">
        <div class="form-group col-xs-8">
          <label for="entry.content">Content</label>
          <textarea id="entry.content" name="content" rows="25" class="form-control"></textarea>
        </div>
      </div>
    </fieldset>

    <input type="submit" value="Create new entry" class="btn btn-primary">
    <a href="${request.referer or request.application_url}" class="btn btn-default">Cancel</a>
  </form>
</%block>
