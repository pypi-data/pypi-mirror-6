{% load variable %}
jQuery(function ($) {
    var
            rules = {},
            messages = {};

    // This is used to ensure validation in hidden fields.
    $.validator.setDefaults({ ignore : [] });

    {% for form_field in form %}
        {% assign field form_field.field %}
        {% assign rules field.validations %}
        rules["{{ form_field.html_name }}"] = {
            {% for name, rule in rules.items %}
                {% if rule.params %}"{{ name }}" : {{ rule.params }}{% if not forloop.last %}, {% endif %}{% endif %}
            {% endfor %}

        };
        messages["{{ form_field.html_name }}"] = {
            {% for name, rule in rules.items %}
                {% if rule.msg %}"{{ name }}" : {{ rule.msg }}{% if not forloop.last %}, {% endif %}{% endif %}
            {% endfor %}
        };
    {% endfor %}
    $('form').attr('novalidate', 'novalidate');
    $.dj.validate("#" + "{{ form_id }}", rules, messages, "{{ validation_base }}");
});