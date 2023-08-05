jQuery(function () {
    var evaluate = function (val, condition, value, type) {
        if (type === "" || type === "string") {
            val = val.toString();
            value = value.toString();
        }

        if (condition === "==" || condition === "") {
            return val === value;
        } else if (condition === "!=") {
            return val !== value;
        } else if (condition === "<") {
            return val < value;
        } else if (condition === ">") {
            return val > value;
        } else if (condition === ">=") {
            return val >= value;
        } else if (condition === "<=") {
            return val <= value;
        }
        return false;
    }, hide_row, show_row;



    {% block form_rule_methods %}
        hide_row = function (elem) {
            elem.parent().parent().hide();
        };

        show_row = function (elem) {
            elem.parent().parent().show();
        };
    {% endblock %}

    {% if debug %}
        if (hide_row === undefined || show_row === undefined) {
            alert("Form rule methods is not valid.");
            throw "Form rule methods is not valid.";
        }
    {% endif %}

    // Hide field rules
    {% for field_name, rule in form.meta_rules.hide_if.items %}
        $("[name=" + "{{ rule.field }}]", main_form).change(function () {
            var elem = $("[name=" + "{{ field_name }}]").parent().parent(),
                    curr = $(this),
                    val = curr.val(),
                    condition = "{{ rule.condition }}",
                    type = "{{ rule.type }}",
                    value = "{{ rule.value }}";

            if (evaluate(val, condition, value, type)) {
                hide_row(elem);
            }
            else {
                show_row(elem);
            }
        });
    {% endfor %}

    // Disable field rules
    {% for field_name, rule in form.meta_rules.disable_if.items %}
        $("[name=" + "{{ rule.field }}]", main_form).change(function () {
            var elem = $("[name=" + "{{ field_name }}]"),
                    curr = $(this),
                    val = curr.val(),
                    condition = "{{ rule.condition }}",
                    type = "{{ rule.type }}",
                    value = "{{ rule.value }}",
                    op = evaluate(val, condition, value, type);
            elem.attr('disabled', op);
        });
    {% endfor %}
});
