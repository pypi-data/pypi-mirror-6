(function () {

    var dj = $.dj || {};
    $.fn.editableform.loading = '<div><i class="icon-spinner icon-spin icon-large"></i></div>';
    dj.xEditable = function (elem, target, url, options, click_elem) {
        var defaults, $elem, $target, $click_elem;

        $elem = $(elem);
        $target = $(target);

        defaults = {
            ajaxOptions : {
                dataType : 'json'
            },
            url : url,
            display : function (value, sourceData, response) {
                if (response === undefined) {
                    response = sourceData;
                }

                if (response && response.msg) {
                    $target.html(response.msg);
                }
            },
            success : function (response) {
                if (response && response.err === true) {
                    return response.msg;
                }
            }
        };

        if (click_elem !== undefined) {
            $click_elem = $(click_elem);
            defaults.toggle = 'manual';
            $click_elem.click(function (e) {
                e.stopPropagation();
                $elem.editable('toggle');
            });

        }

        $.extend(defaults, options);
        $elem.editable(defaults);
    };

}());