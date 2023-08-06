<%!
    import markupsafe
    from pyramid_backend import resources as _rsr
%>
<%inherit file="_layout.mak" />
<%namespace file="_layout.mak" import="data_cell" />

<style type="text/css">
.object-detail .row {
    padding: 0 0.5em;
    border-bottom: 1px solid #eaf2fb;
}
.object-relations .row .value {border-bottom: 1px solid #eaf2fb; margin-bottom: 1em;}
.object-detail .name, .object-relations .name, .object-relations .name {
    font-weight: bold;
    text-align: right;
}
</style>
<%block name="page_title">${backend_mgr.display_name}#${obj} detail</%block>

<%block name="object_detail">
<div class="object-detail">
% for adc in backend_mgr.detail__columns_to_display:
<%
    val = adc.value(obj)
    val_type = view.cell_datatype(val)
%>
    <div class="row col-type-general">
        <div class="col-lg-3 name">${adc.label}</div>
        <div class="col-lg-9 value datatype-${val_type}">${data_cell(val)}</div>
    </div>
% endfor
</%block>
</div>
<legend>Relations</legend>
<div class="object-relations">
% for adc in backend_mgr.detail__relations_to_display:
<% vals = adc.values(obj) %>
<div class="row col-type-general">
    <div class="col-lg-3 name">${adc.label}</div>
    <div class="col-lg-9 value">
        <ul class="list-unstyled">
        % for val in vals:
            <li>
            % if val:
                <a href="${_rsr.object_url(request, val)}">${data_cell(val)}</a>
            % else:
                ${data_cell(val)}
            % endif
            </li>
        % endfor
        </ul>
    </div>
</div>
% endfor
</div>
##
##% if view.relations:
##<legend>Relations</legend>
##<div class="object-relations">
##% for rel_name, rel_model, fk_col in view.relations:
##    <div class="row object-relation">
####        <%
####            if 'query' in rel and rel['query']:
####                query = {}
####                for _name, _value in rel['query'].iteritems():
####                    query[_name] = cur_obj.__getattribute__(_value)
####            else:
####                query = {}
####        %>
##        <div class="col-lg-3 name">
##          <a href="${model_url(rel_model, query={fk_col:cur_obj.id})}">
##            ${' '.join([word.capitalize() for word in rel_name.split('_')])}
##          </a>
##        </div>
##        <% rel_objs = cur_obj.__getattribute__(rel_name) %>
##        <div class="col-lg-9">
####            <div>${len(rel_objs)}</div>
##            <ul class="list-unstyled">
##            % for obj in rel_objs[:10]:
##                <li><a href="${object_url(obj)}">${obj}</a></li>
##            % endfor
##            </ul>
##        </div>
##    </div>
##% endfor
##</div>
##% endif