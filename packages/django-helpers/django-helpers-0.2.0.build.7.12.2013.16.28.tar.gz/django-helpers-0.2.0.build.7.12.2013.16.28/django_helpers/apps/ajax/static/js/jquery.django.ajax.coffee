jQuery ($) ->
    "use strict"

    dj = $.dj = $.dj or {}
    ajax = dj.ajax = dj.ajax or {}

    _block_cache = {}
    _block_names = []
    _blocks = undefined
    _app_name = undefined

    init_blocks = () ->
        _blocks = window.__ajax_blocks
        _app_name = window.__app_name
        for block_name of _blocks
            _block_names.push block_name
        delete window.__ajax_blocks


    init = () ->
        # Assign functions to ajax object
        ajax.load_blocks = load_blocks
        ajax.reload_ajax = reload_ajax
        ajax.has_ajax_blocks = has_ajax_blocks
        ajax.ajaxify = ajaxify
        ajax.can_navigate = can_navigate
        ajax.init_blocks = init_blocks

    get_block = (id)->
        elem = _block_cache[id]
        if not elem
            elem = $("#" + id)
            _block_cache[id] = elem
        elem

    validate_blocks = (block_names)->
        for block_name in block_names
            if block_name not of _blocks
                throw "Invalid AJAX Template Block :" + block_name

    require_js_blocks = (js, callback) ->
        total = js.length
        callback() if total is 0

        count = 0
        require_callback = ()->
            count += 1
            callback() if count is total

        for block in js
            require(block.files, require_callback)


    load_blocks = (url, blocks = _block_names, parent = window) ->
        validate_blocks blocks
        data = $.param
            __blocks__: blocks
            __app_name__: _app_name or ""
        options =
            url: url
            data: data
            type: 'get'
            dataType: 'json'
            headers:
                'X-DJANGO-AJAX-RENDERER': 'true'
            error: () ->
                console.log 'Error occured.'
            success: (obj) ->
                win = window
                js = obj.js
                blocks = obj.blocks

                require_callback = ()->
                    for block_name of blocks
                        block_contents = blocks[block_name]
                        elem = get_block block_name
                        elem.html block_contents

                    for block in js
                        $.globalEval(block.js_code)

                    $(parent).trigger 'djang-ajax-rendered', url, blocks
                    win.location.hash = url
                    document.title = obj.title if obj.title

                require_js_blocks(js, require_callback)

        $.ajax options

    reload_ajax = (blocks = _block_names)->
        load_blocks(@.location, blocks)

    has_ajax_blocks = () ->
        _block_names.length > 0

    ajaxify = (id = window) ->
        $(id).on "click", "a", ()->
            if not has_ajax_blocks()
                console.log "No AJAX Blocks"
                return

            $this = $ @
            href = $this.attr('href')
            if can_navigate(href) is no
                return

            load_blocks href, _block_names, this
            return false

    can_navigate = (url) ->
        first = url[0]

        if first is "#"
            return no

        http = url[0..6]
        https = url[0..7]

        if http is "http://" or https is "https://"
            return no

        return yes


    init()
