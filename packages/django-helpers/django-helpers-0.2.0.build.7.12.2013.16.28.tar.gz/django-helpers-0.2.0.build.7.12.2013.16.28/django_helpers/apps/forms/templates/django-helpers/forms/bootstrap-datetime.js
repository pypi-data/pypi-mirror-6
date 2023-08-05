jQuery(function ($) {
    $('#' + '{{ id }}').datetimepicker({format : '{{ format|default:"yyyy-mm-dd hh:ii" }}'});
});