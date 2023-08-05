{% load jsutils %}
jQuery && jQuery(function ($) {
    if (!$.fn.dataTable) {
        return;
    }
    var oTable, table_id, table;
    table_id = "#" + "{{ table_id }}";

    $("#" + "{{ table_id }}" + "-pagination").remove();
    $("#" + "{{ table_id }}" + "-search").remove();

    table = $(table_id);
    //noinspection JSUnusedLocalSymbols
    oTable = table.dataTable({
        {% if has_form %}
        "sFormID" : {{ form_id|js_string }},
        "fnServerParams" : function (aData) {
            var form_data, len, form_id;
            form_id = "#" + "{{ form_id|safe }}";
            form_data = $(form_id).serializeArray();
            len = form_data.length;
            while (len--) {
                aData.push(form_data[len]);
            }
        },
        {% endif %}

        "bProcessing" : true,
        "bServerSide" : true,
        {% if initial_data %}"iDeferLoading" : {{ total }}, {% endif %}

        "iDisplayLength" : {{ display_length }},
        "aLengthMenu" : [
            {{ display_lengths|js_array }},
            {{ display_lengths|js_array }}
        ],

        {% if ui_themes %}"bJQueryUI" : true, {% endif %}

        /* Make the size drop down multi select */
        "fnInitComplete" : function (oSettings, json) {
            if (!$.fn.multiselect) {
                return;
            }
            var id, wrapper, select;
            id = '{{ table_id }}';
            wrapper = table_id + '_wrapper';

            setTimeout(function () {
                wrapper = $(wrapper);
                select = $('select[name=' + id + '_length]');
                select.multiselect();
            }, 0)

        },

        {% if not bootstrap_theme and not scroller %}
        "sPaginationType" : "full_numbers", {# TODO: Make this a variable #}
        "bPaginate" : true, {# TODO: Make this a variable #}
        {% endif %}

        {% if dom %}
        "sDom" : '{{ dom|safe }}',
        {% endif %}


        {% if scroller %}
        "sScrollY" : "{{ scroller_height }}px",
        "oScroller" : {
            "loadingIndicator" : true {% comment %}Make this to a variable{% endcomment %}
        },
        {% endif %}

        "bDeferRender" : true,
        "sAjaxSource" : "{{ ajax_source }}",
        "aoColumns" : [
            {% for column in columns %}
            {
                "bSortable" : {{ column.sortable|js_bool }},
                "bSearchable" : {{ column.searchable|js_bool }},
                {% if column.title_width %}"sWidth" : "{{ column.title_width }}" {% endif %}
            },
            {% endfor %}
        ],

        "oLanguage" : {
            {% if info_empty %}
            "sZeroRecords" : "{{ info_empty }}",
            {% endif %}
            {% if info_loading %}
            "sLoadingRecords" : "{{ info_loading }}",
            {% endif %}
            {% if info_processing %}
            "sProcessing" : "{{ info_processing|escapejs }}",
            {% endif %}
        }
    });

    {% if is_editable %}
    //noinspection JSUnresolvedFunction
    oTable.Editable(table, {{ editable_columns|js_array }}, '{{ save_source }}');
    {% endif %}

    {% if sql %}
    //noinspection JSUnresolvedFunction
    oTable.sql('#' + '{{ table_id }}' + '-sql');
    {% endif %}

    {% if has_form %}
    $("#" + "{{ form_id }}").on('submit', function () {
        oTable.fnDraw();
        return false;
    });
    {% endif %}

});
