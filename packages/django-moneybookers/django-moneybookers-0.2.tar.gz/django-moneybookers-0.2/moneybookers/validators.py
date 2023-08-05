# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError

from moneybookers.conf import *


def url_target(value):
    if not dict(URL_TARGET).has_key(int(value)):
        raise ValidationError(u'%s is not in URL_TARGET' % value)


def language_code(value):
    if not dict(LANGUAGE_CODE).has_key(value):
        raise ValidationError(u'%s is not in LANGUAGE_CODE' % value)


def customer_title(value):
    if not dict(CUSTOMER_TITLE).has_key(value):
        raise ValidationError(u'%s is not in CUSTOMER_TITLE' % value)


def country_code(value):
    if not dict(ISO3166_A3).has_key(value):
        raise ValidationError(u'%s is not in ISO3166_A3' % value)


def valuta_code(value):
    if not dict(ISO4217).has_key(value):
        raise ValidationError(u'%s is not in ISO4217' % value)
