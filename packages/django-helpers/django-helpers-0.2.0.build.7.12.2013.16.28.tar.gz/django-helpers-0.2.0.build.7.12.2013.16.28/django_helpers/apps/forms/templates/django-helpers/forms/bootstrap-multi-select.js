jQuery(function ($) {
    $('#' + '{{ id }}').multiselect({
        buttonClass : '{{ button_class }}',
        buttonWidth : '{{ button_width }}',

        {% if button_container %}buttonContainer : '{{ button_container }}',{% endif %}

        selectedClass : '{{ selected_class }}',

        // maxHeight : '{{ max_height }}',

        includeSelectAllOption : {{ include_select_all_option }},
        {% if select_all_text %}selectAllText : {{ select_all_text }},{% endif %}
        {% if select_all_value %}selectAllValue : '{{ select_all_value }}',{% endif %}

        enableFiltering : {{ enable_filtering }},

        filterPlaceholder : '{{ filter_placeholder }}',

        dropRight : {{ drop_right }}
    });
});