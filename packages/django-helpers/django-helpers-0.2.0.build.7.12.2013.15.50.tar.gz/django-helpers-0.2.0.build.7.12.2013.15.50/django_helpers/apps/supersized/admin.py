# coding=utf-8
__author__ = 'ajumell'

from django.contrib.admin import site
from models import SuperSizedSlide, SuperSizedSlider

site.register(SuperSizedSlide)
site.register(SuperSizedSlider)