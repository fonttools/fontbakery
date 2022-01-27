var checkTemplate = Handlebars.compile(`
    <div class="card my-4">
      <div class="card-header">
        <code>{{id}}</code>
      </div>
      <div class="card-body">
        <a name="{{id}}"><h2> {{check.description}} </h2></a>
        {{{check.rationale}}}
        <table class="table">
        {{#if check.proposal}}
        <a href="{{check.proposal}}">More information</a>
        {{/if}}

        {{#if check.severity}}
        <tr><th>Severity</th><td>{{check.severity}}</td></tr>
        {{/if}}
        <tr>
          <th>Sections</th>
          <td>
          {{# each check.sections}}
            <span class="badge rounded-pill bg-primary"> {{this}} </span>
            {{/each}}
          </td>
        </tr>
        <tr>
          <th>Profiles</th>
          <td>
          {{# each check.profiles}}
            <span class="badge rounded-pill bg-primary"> {{this}} </span>
            {{/each}}
          </td>
        </tr>
        </table>
      </div>
    </div>
`);

function render() {
  var ids = Object.keys(window.fbchecks);
  ids.sort();
  for (id of ids) {
    feat = window.fbchecks[id];
    var checkdiv = $(checkTemplate({ id: id, check: feat }));
    $("#checks").append(checkdiv);
  }
}

$(render);
