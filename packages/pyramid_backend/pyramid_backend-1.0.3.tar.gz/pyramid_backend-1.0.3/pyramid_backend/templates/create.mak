<%inherit file="_layout.mak"/>

<%block name="page_title">Create new ${request.context.model.__backend_manager__.display_name}</%block>

<%block name="form_block">${form.render()|n}</%block>