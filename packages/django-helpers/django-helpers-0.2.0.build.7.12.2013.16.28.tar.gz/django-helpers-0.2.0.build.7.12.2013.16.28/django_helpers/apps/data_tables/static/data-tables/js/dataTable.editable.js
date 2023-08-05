(function ($) {
    if (typeof $.fn.dataTable == "function" && typeof $.fn.dataTableExt.fnVersionCheck == "function" && $.fn.dataTableExt.fnVersionCheck('1.9.0')) {

        var makeEditable = function (oTable, columns, url, table) {
            var options, len;
            options = {
                "submitdata" : function (value, settings) {
                    return {
                        "row_id" : this.parentNode.getAttribute('id'),
                        "column" : oTable.fnGetPosition(this)[2]
                    };
                },
                "height" : "auto",
                "indicator" : '<i class="icon-spinner icon-spin icon-large"></i>Saving data...'
            };

            len = columns.length;
            while (len--) {
                $('td:nth-child(' + columns[len] + ')', table).editable(url, options);
            }
        };

        $.fn.dataTableExt.oApi.Editable = function (oSettings, table, columns, ajax_url) {
            var oTable = this;
            this.bind('draw', function (e, s) {
                makeEditable(oTable, columns, ajax_url, table);
            });
            makeEditable(oTable, columns, ajax_url, table);
        }
    }
})(jQuery);
