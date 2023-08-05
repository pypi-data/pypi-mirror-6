# coding=utf-8
from django_helpers.helpers.views import render_to_string
from django_helpers.apps.static_manager import add_css_file, jQueryURL
from django_helpers.templatetags.jsutils import js_bool

__author__ = 'ajumell'


class Effects(object):
    sliceDown = "sliceDown"
    sliceDownLeft = "sliceDownLeft"
    sliceUp = "sliceUp"
    sliceUpLeft = "sliceUpLeft"
    sliceUpDown = "sliceUpDown"
    sliceUpDownLeft = "sliceUpDownLeft"
    fold = "fold"
    fade = "fade"
    random = "random"
    slideInRight = "slideInRight"
    slideInLeft = "slideInLeft"
    boxRandom = "boxRandom"
    boxRain = "boxRain"
    boxRainReverse = "boxRainReverse"
    boxRainGrow = "boxRainGrow"
    boxRainGrowReverse = "boxRainGrowReverse"


class Themes(object):
    bar = "bar"
    light = "light"
    dark = "dark"
    default = "default"
    wds = "wds"


ThemesChoices = []
EffectsChoices = []

for item in dir(Effects):
    if not item.startswith('__'):
        val = getattr(Effects, item)
        if EffectsChoices.count(val) == 0:
            EffectsChoices.append((item, val))

for item in dir(Themes):
    if not item.startswith('__'):
        val = getattr(Themes, item)
        if ThemesChoices.count(val) == 0:
            ThemesChoices.append((item, val))


class NivoSliderSlide(object):
    def __init__(self, url, caption=None, alternate_text="", link=None, transition=None):
        self.url = url
        self.link = link
        self.alternate_text = alternate_text
        self.caption = caption
        self.transition = transition


def use_theme(name):
    add_css_file('nivo-slider/css/themes/%s/%s.css' % (name, name))


class NivoSlider(object):
    width = None
    height = None

    slider_id = None
    effect = 'random'
    slices = 15
    box_cols = 8
    box_rows = 4
    animation_speed = 700
    pause_time = 3000
    start_slide = 0
    direction_nav = True
    control_nav = True
    control_bav_thumbs = False
    pause_on_hover = True
    manual_advance = False
    prev_text = 'Prev'
    next_text = 'Next'
    random_start = False
    images = []
    theme_name = "bar"
    css_class = ""

    def __init__(self):
        # Prevent duplicate slides in each request
        self.images = self.images[:]
        self.js_files = [jQueryURL, 'nivo-slider/js/jquery.nivo.slider.pack.js']
        add_css_file('nivo-slider/css/nivo-slider.css')

        self.theme = self.theme_name

    def add_image(self, url, caption=None, alternate_text="", link=None, transition=None):
        self.images.append(NivoSliderSlide(url, caption, alternate_text, link, transition))

    @property
    def theme(self):
        return self.theme_name

    @theme.setter
    def theme(self, val):
        use_theme(val)
        self.theme_name = val

    def render(self):
        if not self.slider_id:
            raise Exception("Slider ID is require.")

        class_name = "nivoSlider"
        if self.css_class:
            class_name = class_name + " " + self.css_class

        return render_to_string('nivo-slider/nivo-slider.html', {
            "theme": self.theme_name,
            "width": self.width,
            "height": self.height,
            "class_name": class_name,
            "images": self.images,
            "slider_id": self.slider_id,
            "effect": self.effect,
            "slices": self.slices,
            "box_cols": self.box_cols,
            "box_rows": self.box_rows,
            "animation_speed": self.animation_speed,
            "pause_time": self.pause_time,
            "start_slide": self.start_slide,
            "direction_nav": js_bool(self.direction_nav),
            "control_nav": js_bool(self.control_nav),
            "control_nav_thumbs": js_bool(self.control_bav_thumbs),
            "pause_on_hover": js_bool(self.pause_on_hover),
            "manual_advance": js_bool(self.manual_advance),
            "prev_text": self.prev_text,
            "next_text": self.next_text,
            "random_start": js_bool(self.random_start)
        })

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render()

    def css_files(self):
        pass