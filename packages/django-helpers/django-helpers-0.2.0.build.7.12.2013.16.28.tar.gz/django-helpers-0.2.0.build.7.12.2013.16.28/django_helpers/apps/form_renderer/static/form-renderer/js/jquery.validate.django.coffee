$.dj = $.dj or {}

jQuery ($) ->
    elementValue = (element) ->
        $elem = $ element
        type = $elem.attr("type")
        val = $elem.val()
        if type is "radio" or type is "checkbox"
            sel = "input[name='" + $elem.attr("name") + "']:checked"
            val = $(sel).val()
            return val
        return val.replace(/\r/g, "")  if typeof val is "string"
        val

    $.dj.msgs =
        sprintf_length: (msg) ->
            (params, element) ->
                value = elementValue(element).length
                obj =
                    limit_value: params
                    show_value: value

                sprintf msg, obj

        sprintf_value: (msg) ->
            (params, element) ->
                value = elementValue(element)
                obj =
                    limit_value: params
                    show_value: value

                sprintf msg, obj

        sprintf_params: (msg) ->
            (params) ->
                sprintf msg, params

jQuery ($) ->
    validator = $.validator

    get_digits = (val) ->
        i = val.indexOf(".")
        return val  if i is -1
        val.substr 0, i

    get_decimals = (val) ->
        i = val.indexOf(".")
        return ""  if i is -1
        val.substr i + 1

    validator.addMethod "integer", (value, element, params) ->
        return true  if @optional(element)
        return true  unless params
        new_val = parseInt(value, 10)
        new_val + "" is value

    validator.addMethod "max_digits", (value, element, params) ->
        return true  if @optional(element)
        digits = get_digits(value)
        decimals = get_decimals(value)
        digits.length + decimals.length <= params

    validator.addMethod "max_decimal_places", (value, element, params) ->
        return true  if @optional(element)
        decimals = get_decimals(value)
        decimals.length <= params

    validator.addMethod "max_whole_digits", (value, element, params) ->
        return true  if @optional(element)
        digits = get_digits(value)
        digits.length <= params

    validator.addMethod "math", (value, element) ->
        true  if @optional(element)


jQuery ($) ->
    valueCaches = {}
    defaultCache = {}
    $.dj = {}  if $.dj is undefined
    dj = $.dj
    getCache = (name) ->
        valueCaches[name] = {}  if valueCaches[name] is undefined
        valueCaches[name]

    setValue = (name, val, override, cache_name) ->
        cache = getCache(cache_name)
        if cache[name] is undefined or override is true
            cache[name] = val
        else throw "Already exists."  if cache[name] isnt undefined

    getValueSetter = (cache_name) ->
        (name, val, override) ->
            setValue name, val, override, cache_name

    getValue = (name, cache_name, d) ->
        cache = getCache(cache_name)
        val = cache[name]
        val = defaultCache[cache_name]  if val is undefined and d is true
        val

    getValueGetter = (cache_name) ->
        (name, base, options) ->
            val = getValue(name, cache_name, base is undefined)
            val = getValue(name, base, cache_name)  if val is undefined and base isnt undefined
            options[cache_name] = val  if val isnt undefined
            val

    dj.setErrorPlacement = getValueSetter("errorPlacement")
    dj.setSuccess = getValueSetter("success")
    dj.setHighlight = getValueSetter("highlight")
    dj.setErrorClass = getValueSetter("errorClass")
    dj.setValidClass = getValueSetter("validClass")
    dj.setErrorElement = getValueSetter("errorElement")

    getErrorPlacement = getValueGetter("errorPlacement")
    getSuccess = getValueGetter("success")
    getHighlight = getValueGetter("highlight")
    getErrorClass = getValueGetter("errorClass")
    getValidClass = getValueGetter("validClass")
    getErrorElement = getValueGetter("errorElement")

    dj.setDefault = (name, val, override) ->
        if defaultCache[name] is undefined or override
            defaultCache[name] = val
        else throw "Already exists."  if defaultCache[name] isnt undefined

    dj.validate = (form_id, rules, messages, validation_base) ->
        validation_base = undefined  if validation_base is ""
        form = $(form_id)
        options =
            rules: rules
            messages: messages

        getErrorElement form_id, validation_base, options
        getErrorClass form_id, validation_base, options
        getErrorPlacement form_id, validation_base, options
        getSuccess form_id, validation_base, options
        getHighlight form_id, validation_base, options
        getValidClass form_id, validation_base, options

        form.validate options
