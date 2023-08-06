<%inherit file="_layout.mak"/>

<%block name="page_title">Update ${request.context.model.__backend_manager__.display_name}#${obj}</%block>

<%block name="form_block">${form.render()|n}</%block>