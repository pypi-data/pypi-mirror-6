<%inherit file="/reports/base.mako" />

<%def name="title()">Report : Inventory Worksheet</%def>

<p>Please provide the following criteria to generate your report:</p>
<br />

${h.form(request.current_route_url())}

<div class="field-wrapper">
  <label for="department">Department</label>
  <div class="field">
    <select name="department">
      % for department in departments:
          <option value="${department.uuid}">${department.name}</option>
      % endfor
    </select>
  </div>
</div>

<div class="field">
  ${h.checkbox('weighted-only', label=h.literal("Include items sold by weight <strong>only</strong>."))}
</div>

<div class="buttons">
  ${h.submit('submit', "Generate Report")}
</div>

${h.end_form()}
