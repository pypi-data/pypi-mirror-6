$.dj = $.dj || {};
jQuery(function ($) {
    var
        elementValue = function (element) {
            var type = $(element).attr("type"),
                val = $(element).val();
            if (type === "radio" || type === "checkbox") {
                return $("input[name='" + $(element).attr("name") + "']:checked").val();
            }
            if (typeof val === "string") {
                return val.replace(/\r/g, "");
            }
            return val;
        };


    $.dj.msgs = {

        'sprintf_length' : function (msg) {
            return function (params, element) {
                var value = elementValue(element).length;
                var obj = {
                    'limit_value' : params,
                    'show_value' : value
                };
                return sprintf(msg, obj);
            };
        },

        'sprintf_value' : function (msg) {
            return function (params, element) {
                var value = elementValue(element);
                var obj = {
                    'limit_value' : params,
                    'show_value' : value
                };
                return sprintf(msg, obj);
            };
        },


        'sprintf_params' : function (msg) {
            return function (params, element) {
                return sprintf(msg, params);
            };
        }
    };
});

jQuery(function ($) {
    var validator = $.validator,
        get_digits,
        get_decimals;

    get_digits = function (val) {
        var i = val.indexOf('.');
        if (i === -1) {
            return val;
        }
        return val.substr(0, i);
    };

    get_decimals = function (val) {
        var i = val.indexOf('.');
        if (i === -1) {
            return '';
        }
        return val.substr(i + 1);
    };

    validator.addMethod("integer", function (value, element, params) {
        if (this.optional(element)) {
            return true;
        }
        if (!params) {
            return true;
        }
        var new_val = parseInt(value, 10);
        return new_val + "" === value;
    });

    validator.addMethod("max_digits", function (value, element, params) {
        if (this.optional(element)) {
            return true;
        }
        var digits, decimals;

        digits = get_digits(value);
        decimals = get_decimals(value);
        return digits.length + decimals.length <= params;
    });

    validator.addMethod("max_decimal_places", function (value, element, params) {
        if (this.optional(element)) {
            return true;
        }
        var decimals;

        decimals = get_decimals(value);
        return decimals.length <= params;
    });

    validator.addMethod("max_whole_digits", function (value, element, params) {
        if (this.optional(element)) {
            return true;
        }
        var digits;

        digits = get_digits(value);
        return digits.length <= params;
    });

    validator.addMethod("math", function (value, element, params) {
        if (this.optional(element)) {
            return true;
        }

    });

});

jQuery(function ($) {

    var
        dj,
        valueCaches = {},
        defaultCache = {},

        getCache,

        setValue,
        getValueSetter,

        getValue,
        getValueGetter,

        getErrorPlacement,
        getSuccess ,
        getHighlight ,
        getErrorClass,
        getValidClass,
        getErrorElement;

    if ($.dj === undefined) {
        $.dj = {};
    }
    dj = $.dj;

    getCache = function (name) {
        if (valueCaches[name] === undefined) {
            valueCaches[name] = {};
        }
        return valueCaches[name];
    };

    setValue = function (name, val, override, cache_name) {
        var cache = getCache(cache_name);
        if (cache[name] === undefined || override === true) {
            cache[name] = val;
        } else if (cache[name] !== undefined) {
            throw "Already exists.";
        }
    };

    getValueSetter = function (cache_name) {
        return function (name, val, override) {
            return setValue(name, val, override, cache_name);
        };
    };

    getValue = function (name, cache_name, d) {
        var cache = getCache(cache_name),
            val = cache[name];
        if (val === undefined && d === true) {
            val = defaultCache[cache_name];
        }
        return val;
    };

    getValueGetter = function (cache_name) {
        return function (name, base, options) {
            var val = getValue(name, cache_name, base === undefined);
            if (val === undefined && base !== undefined) {
                val = getValue(name, base, cache_name);
            }
            if (val !== undefined) {
                options[cache_name] = val;
            }
            return val;
        };
    };

    dj.setErrorPlacement = getValueSetter("errorPlacement");
    dj.setSuccess = getValueSetter("success");
    dj.setHighlight = getValueSetter("highlight");
    dj.setErrorClass = getValueSetter("errorClass");
    dj.setValidClass = getValueSetter("validClass");
    dj.setErrorElement = getValueSetter("errorElement");

    getErrorPlacement = getValueGetter("errorPlacement");
    getSuccess = getValueGetter("success");
    getHighlight = getValueGetter("highlight");
    getErrorClass = getValueGetter("errorClass");
    getValidClass = getValueGetter("validClass");
    getErrorElement = getValueGetter("errorElement");

    dj.setDefault = function (name, val, override) {
        if (defaultCache[name] === undefined || override) {
            defaultCache[name] = val;
        } else if (defaultCache[name] !== undefined) {
            throw 'Already exists.';
        }

    };

    dj.validate = function (form_id, rules, messages, validation_base) {
        var form, options;

        if (validation_base === "") {
            validation_base = undefined;
        }

        form = $(form_id);
        options = {
            rules : rules,
            messages : messages
        };

        getErrorElement(form_id, validation_base, options);
        getErrorClass(form_id, validation_base, options);
        getErrorPlacement(form_id, validation_base, options);
        getSuccess(form_id, validation_base, options);
        getHighlight(form_id, validation_base, options);
        getValidClass(form_id, validation_base, options);

        form.validate(options);
    };

});