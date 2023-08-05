# coding=utf-8
from json import dumps
from hashlib import md5

from django.core.urlresolvers import reverse
from django.core.validators import *
from django.forms import *
from django.utils.html import escapejs
from django.utils.safestring import mark_safe

from django_helpers.helpers.views import render_json
from django_helpers.apps.static_manager import jQueryURL


__all__ = (
    'validation_preprocessor',
    'register'
)

SPRINTF_PARAMS = 'sprintf_params'
SPRINTF_VALUE = 'sprintf_value'
SPRINTF_LENGTH = 'sprintf_length'


def params(obj):
    """
    Returns the safe string json of the given object.
    @param obj:
    @return:
    """
    return mark_safe(dumps(obj))


def generate_rule(obj, msg):
    """
    Returns a dictionary with the given message and parameter.
    @param obj:
    @param msg:
    @return:
    """
    return {
        'params': params(obj),
        'msg': msg
    }


def wrap_str(display_message, function):
    return mark_safe(u'$.dj.msgs.' + function + u'(' + unicode(display_message) + u')')


def wrap_message(rule, function):
    msg = rule['msg']
    rule['msg'] = wrap_str(msg, function)


def err_msg(msg, function=None):
    msg = '"' + unicode(escapejs(msg)) + '"'
    if function is not None:
        msg = wrap_str(msg, function)
    else:
        msg = mark_safe(msg)
    return msg


def msg(validator, error_messages, function=None):
    error_message = validator.message or error_messages.get(validator.code)
    return err_msg(error_message, function)


def validation_preprocessor(renderer):
    """
    @type renderer: django_helpers.apps.form_renderer.FormRenderer()
    @param renderer:
    """

    js_files = [
        jQueryURL,
        'form-renderer/js/jquery.validate.js',
        'form-renderer/js/sprintf.min.js',
        'form-renderer/js/jquery.validate.django.js'
    ]

    renderer.add_js_requirement(js_files)

    form = renderer.form
    ignorable_custom_validations = getattr(renderer, 'ignorable_custom_validations', [])
    for name, field in form.fields.items():
        validations = getattr(field, 'validations', None) or {}
        error_messages = field.error_messages

        if field.required:
            validations['required'] = generate_rule(True, err_msg(error_messages['required']))

        if isinstance(field, DateField):
            validations['date'] = generate_rule(True, err_msg(error_messages['invalid']))

        if isinstance(field, IntegerField):
            validations['integer'] = generate_rule(True, err_msg(error_messages['invalid']))

        if isinstance(field, DecimalField):
            validations['number'] = generate_rule(True, err_msg(error_messages['invalid']))

            digits = field.max_digits
            decimals = field.decimal_places

            if digits is not None:
                m = err_msg(error_messages['max_digits'], SPRINTF_PARAMS)
                validations['max_digits'] = generate_rule(digits, m)

            if decimals is not None:
                m = err_msg(error_messages['max_decimal_places'], SPRINTF_PARAMS)
                validations['max_decimal_places'] = generate_rule(decimals, m)

            if decimals is not None and digits is not None:
                whole_nums = digits - decimals
                m = err_msg(error_messages['max_whole_digits'], SPRINTF_PARAMS)
                validations['max_whole_digits'] = generate_rule(whole_nums, m)

        if isinstance(field, FloatField):
            validations['number'] = generate_rule(True, err_msg(error_messages['invalid']))

        if hasattr(form, 'clean_%s' % name) and name not in ignorable_custom_validations:
            dt = {
                'url': reverse('validate-form'),
                'type': 'get',
                'data': {
                    'form_id': register_form(form),
                    'field_name': name
                }
            }
            validations['remote'] = generate_rule(dt, '')

        for validator in field.validators:

            obj = getattr(validator, 'limit_value', True)
            error_message = msg(validator, error_messages)
            rule = generate_rule(obj, error_message)

            if isinstance(validator, EmailValidator):
                wrap_message(rule, SPRINTF_VALUE)
                validations['email'] = rule

            elif isinstance(validator, URLValidator):
                validations['url'] = rule

            elif isinstance(validator, MinLengthValidator):
                wrap_message(rule, SPRINTF_LENGTH)
                validations['minlength'] = rule

            elif isinstance(validator, MaxLengthValidator):
                wrap_message(rule, SPRINTF_LENGTH)
                validations['maxlength'] = rule

            elif isinstance(validator, MinValueValidator):
                wrap_message(rule, SPRINTF_VALUE)
                validations['min'] = rule

            elif isinstance(validator, MaxValueValidator):
                wrap_message(rule, SPRINTF_VALUE)
                validations['max'] = rule

            elif isinstance(validator, RegexValidator):
                validations['regex'] = generate_rule(validator.regex.pattern, error_message)
                continue

        setattr(field, 'validations', validations)
    template = getattr(renderer, 'validation_template', 'form-renderer/preprocessors/validations.js')
    renderer.js_templates.append(template)


def remote_validation_preprocessor(renderer):
    form = renderer.form
    datas = getattr(renderer, 'remote_validations', None)

    if type(datas) is not dict:
        return

    for name, data in datas.items():
        field = form.fields[name]
        validations = getattr(field, 'validations', None) or {}
        if 'remote' in validations:
            raise Exception('Remote validation already exists.')
        if type(data) in (list, tuple):
            url = reverse(*data)
        elif type(data) is dict:
            url = reverse(**data)
        else:
            url = reverse(data)
        validations['remote'] = {
            'params': url
        }
        setattr(field, 'validations', validations)


#
#   Custom Validation
#
lookup = {}

_register_key = '__custom_validation_id__'


def register(cls):
    form_id = getattr(cls, _register_key, None)

    if form_id is None:
        form_id = md5(unicode(cls)).hexdigest()
        setattr(cls, _register_key, form_id)

    if form_id not in lookup:
        lookup[form_id] = cls

    return cls


def register_form(form):
    cls = type(form)
    form_id = getattr(cls, _register_key, None)
    if form_id is None:
        raise Exception("Form not registered for custom validation")

    if form_id not in lookup:
        raise Exception("Form not registered for custom validation")

    return form_id


def get_form(form_id, post_data):
    cls = lookup.get(form_id)
    if cls is None:
        return None
    return cls(post_data)


def validate_form(request):
    post = request.GET
    form_id = post.get('form_id')
    field_name = post.get('field_name')
    form = get_form(form_id, post)
    if form is None:
        return render_json("Server error.")

    errors = form.errors
    if field_name in errors:
        return render_json('<br />'.join(errors[field_name]))
    return render_json(True)
