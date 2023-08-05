jQuery(function ($) {
    $('#' + '{{ id }}').datepicker({
        weekStart : {{ week_start }},
        format : '{{ format|default:"yyyy-mm-dd hh:ii" }}',
        calendarWeeks : {{ calendar_weeks }},
        {% if start_date %}
            startDate : {{ start_date }},
        {% endif %}
        {% if end_date %}
            endDate : {{ end_date }},
        {% endif %}
        {% if day_of_week_disabled %}
            daysOfWeekDisabled : {{ day_of_week_disabled }},
        {% endif %}
        autoclose : {{ auto_close }},
        startView : {{ start_view }},
        minViewMode : {{ min_view_mode }},
        todayBtn : {{ today_btn }},
        todayHighlight : {{ today_highlight }},
        keyboardNavigation : {{ keyboard_navigation }},
        language : '{{ language }}',
        forceParse : {{ force_parse }}

    });
});