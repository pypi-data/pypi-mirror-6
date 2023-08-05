jQuery(function ($) {
    var id, menu;
    id = "{{ menu_id }}";
    menu = $("#" + id);

    menu.superfish({
        pathClass : 'active'
    });

    $.dj.ajax.ajaxify("#" + id);
    $('a', menu).on('djang-ajax-rendered', function () {
        var li, ul;
        menu.find('.active').removeClass('active');
        li = $(this).parent('li');
        while (true) {
            li.addClass('active');
            ul = li.parent('ul');
            if (ul.attr('id') == id) {
                break;
            }
            li = ul.parent('li');
        }
    });

});
