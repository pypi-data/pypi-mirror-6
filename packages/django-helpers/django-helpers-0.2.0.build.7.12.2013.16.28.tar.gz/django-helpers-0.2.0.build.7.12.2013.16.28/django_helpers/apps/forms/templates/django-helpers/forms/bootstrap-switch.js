jQuery(function ($) {
    var obj, container, yes, no;

    obj = $('#' + '{{ id }}');
    container = $('<div class="switch" />');

    yes = '{{ yes|escapejs }}';
    no = '{{ no|escapejs }}';

    if (yes) {
        container.attr('data-on-label', yes);
    }

    if (no) {
        container.attr('data-off-label', no)
    }

    obj.wrap(container).parent().bootstrapSwitch();
});