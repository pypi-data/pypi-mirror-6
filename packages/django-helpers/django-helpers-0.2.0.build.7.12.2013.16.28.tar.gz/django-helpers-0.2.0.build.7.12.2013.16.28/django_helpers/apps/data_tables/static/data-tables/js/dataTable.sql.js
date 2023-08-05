(function ($) {
    if (typeof $.fn.dataTable == "function" && typeof $.fn.dataTableExt.fnVersionCheck == "function" && $.fn.dataTableExt.fnVersionCheck('1.9.0')) {
        $.fn.dataTableExt.oApi.sql = function (oSettings, sql_id) {
            var sql_elem = $(sql_id);
            this.bind('xhr', function (e, s, json) {
                sql_elem.html(json.sql).removeClass('prettyprinted');
                window.prettyPrint && prettyPrint();
            });
            window.prettyPrint && prettyPrint();
        }
    }
})(jQuery);
