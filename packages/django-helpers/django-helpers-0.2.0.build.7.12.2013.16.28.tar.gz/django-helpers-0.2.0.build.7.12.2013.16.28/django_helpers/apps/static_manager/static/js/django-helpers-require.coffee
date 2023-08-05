jQuery ($) ->

    ###* 
        @author Muhammed K K
        @date-created 22/7/13, 3:46 PM
        The list of already loaded files.
    ###
    __loaded_files = []

    ###*
        @author Muhammed K K
        @date-created 22/7/13, 3:46 PM
        List of files witing to be loaded.
    ###
    __waiting_list = []

    ###* 
        @author Muhammed K K
        @date-created 22/7/13, 3:46 PM
        Dictionary which has all the callbacks registered for a
        Javascript file.
    ###
    __callbacks = {}

    ###*
        @author Muhammed K K
        @date-created 22/7/13, 3:47 PM
        A list of already evaluated Javascript Files.
    ###
    __evaluated_files = []

    ###*
        @author Muhammed K K
        @date-created 22/7/13, 3:48 PM
        Register a callback for a Javascript file.
        When the file is loaded all the callbacks
        will be executed.
    ###
    add_callback = (js, callback)->
        callbacks = __callbacks[js]
        if not callbacks
            callbacks = []
            __callbacks[js] = callbacks
        callbacks.push callback

    ###*
        @author Muhammed K K
        @date-created 22/7/13, 3:50 PM
        Executes the loaded js file and adds it to a list of executed files.
    ###
    evaluate = (js, code)->
        if js in __evaluated_files
            return
        $.globalEval code
        __evaluated_files.push js

    ###*
        @author Muhammed K K
        @date-created 22/7/13, 3:51 PM
        Invokes the callbacks for the javascript the given
        javascript file and removes it from the queue.
    ###
    invoke_callbacks = (js, content) ->
        callbacks = __callbacks[js]
        for callback in callbacks
            callback(js, content)
        delete __callbacks[js]

    load_js = (js, callback) ->
        if js in __loaded_files
            return callback(js, undefined)

        add_callback js, callback
        if js in __waiting_list
            return

        __waiting_list.push js
        $.get js, (contents) ->
            i = __waiting_list.indexOf js
            __waiting_list.splice i, 1
            __loaded_files.push js
            invoke_callbacks(js, contents)

    require = (js_files, callback) ->
        current = 0
        total = js_files.length
        callback() if total is 0
        loaded_data = {}
        js_loadede = (js, loaded_contents) ->
            loaded_data[js] = loaded_contents
            current += 1
            if current is total
                for js in js_files
                    contents = loaded_data[js]
                    if contents
                        delete loaded_data[js]
                        evaluate(js, contents)
                callback()
        for js in js_files
            load_js js, js_loadede

    window.require = require