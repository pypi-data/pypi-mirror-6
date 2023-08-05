$.dj.xEditable("#" + '{{ field_id }}', "#" + '{{ field_id }}', '{{ save_url }}', {
    pk : '{{ pk }}',
    title : '{{ title }}',
    name : '{{ name }}',
    placement : 'top',
    type : 'date',

    viewformat: '{{ view_format }}',
    format: '{{ date_format }}'

});