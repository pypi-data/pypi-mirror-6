(function (w) {
    w.__ajax_blocks = {
        {% for block in blocks %}
        "{{ block.0 }}" : "{{ block.1 }}"{% if not forloop.last %}, {% endif %}
        {% endfor %}
    };
    $.dj.ajax.init_blocks();
}(window));