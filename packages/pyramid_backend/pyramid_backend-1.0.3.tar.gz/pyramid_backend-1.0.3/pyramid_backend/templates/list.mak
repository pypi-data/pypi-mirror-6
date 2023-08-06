<%! from pyramid_backend import resources as _rsr %>
<%inherit file="_layout.mak"/>
<%namespace file="_layout.mak" import="cmd_button, data_cell"/>

<%block name="page_title">${backend_mgr.display_name} list</%block>

<%block name="object_list">
<table class="table table-striped table-bordered table-condensed table-objects">
    <thead>
        <tr>
            <th>Commands</th>
            % for adc in backend_mgr.list__columns_to_display:
            <th class="">${adc.label}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
    % for e in page.items:
        <tr>
            <td class="col-type-commands">
                % for cmd in view.object_actions(e):
                ${cmd_button(cmd)}
                % endfor
            </td>
        % for adc in backend_mgr.list__columns_to_display:
            <%
                val = adc.value(e)
                val_type = view.cell_datatype(val)
            %>
            % if adc.attr_name == backend_mgr.id_attr:
                <td class="datatype-${val_type}"><a href="${_rsr.object_url(request, e)}">${val}</a></td>
            % else:
            <td class="datatype-${val_type}">${data_cell(val)}</td>
            % endif
        % endfor
        </tr>
    % endfor
    </tbody>
</table>
</%block>

<%block name="object_paging">
<%
    import re
    pager_html = page.pager(
        format='(Page $page of $page_count) &nbsp;&nbsp; <ul class="pagination pagination-sm">$link_first~3~$link_last</ul>',
        dotdot_attr={"class":"disabled"},
        curpage_attr={"class":"current-page"},
        symbol_first=u'«',
        symbol_last=u'»',
    )

    ## replace current page link
    pager_html = unicode(pager_html)
    pager_html = re.sub(
        r'<span[^>]+class="current-page">(.*?)</span>',
        r'<li class="active"><a href="#">\1 <span class="sr-only">(current)</span></a></li>',
        pager_html)
    pager_html = re.sub(
        r'<a[^>]+class="pager_link"[^>]+href="([^"]*)">(.*?)</a>',
        r'<li><a href="\1">\2</a></li>',
        pager_html)
    pager_html = re.sub(
        r'<span[^>]+class="disabled"[^>]*>(.*?)</span>',
        r'<li class="disabled"><span>\1</span></li>',
        pager_html)
%>
${pager_html|n}
</%block>