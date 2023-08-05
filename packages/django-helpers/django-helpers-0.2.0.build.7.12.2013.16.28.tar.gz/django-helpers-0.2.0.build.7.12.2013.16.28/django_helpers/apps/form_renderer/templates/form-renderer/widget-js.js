{% for field in form %}
    {% if field.field.widget.has_js %}
        {{ field.field.widget.render_js }}
    {% endif %}
{% endfor %}


{% if focus_first %}
jQuery(function ($) {
    $("input:first").focus();
});
{% endif %}
