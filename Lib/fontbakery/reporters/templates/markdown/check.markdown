<details>
    <summary>{{check.result | emoticon}} <b>{{check.result}}</b> {{check.description}} <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/{{check.module}}.html#{{check.id | replace("_", "-") | replace("/", "-") | replace(".", "-")}}">{{check.id}}</a></summary>
    <div>

{% if not succinct and check.rationale %}
{% for line in check.rationale.split("\n") %}> {{line | unwrap | replace("\n", "") }}
{% endfor %}
{% endif %}

{% if check.proposal and not succinct %}
{% for proposal in check.proposal %}{% if loop.index == 1 %}> Original proposal: {{proposal}}
{% else %}> See also: {{proposal}}
{%endif%}{% endfor %}
{% endif %}

{% for result in check.logs |sort(attribute="status") %}
{% if not result is omitted %}
* {{result.status | emoticon }} **{{result.status}}** {{result.message.message | markdown}} {%if result.message.code%}[code: {{result.message.code}}]{%endif%}
{% endif %}
{% endfor %}

</div>
</details>