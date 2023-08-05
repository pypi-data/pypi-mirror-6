from django.shortcuts import render
from django_helpers.helpers.views import render_json


def register_ajax():
    pass


# noinspection PyUnusedLocal
def render_form(request, name):
    pass


def render_for_modal(request, Form=None):
    method = request.method
    form = Form(request.POST or None)
    if method == 'POST':
        if not request.is_ajax():
            raise Exception("Hack attempt")

        if form.is_valid():
            obj = form.save()
            return render_json({
                'id': obj.id,
                'value': str(obj)
            })
    return render(request, 'modal_render.html', {
        "form": form
    })