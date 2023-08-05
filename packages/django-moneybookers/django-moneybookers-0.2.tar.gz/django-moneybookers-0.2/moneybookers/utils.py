# -*- coding: utf-8 -*-
from hashlib import md5
from datetime import datetime
from random import random

from moneybookers.conf import SECRET_WORD, MERCHANT_ID
from moneybookers.models import MoneybookersTransaction


def md5merchant_generate(user_id, invoice, amount, merchant_field_value):
    if not user_id:
        user_id = ""
    if not invoice:
        invoice = ""
    if not amount:
        amount = ""
    if not merchant_field_value:
        merchant_field_value = ""
    s = u"%s%s%s%s%s" % (user_id, invoice, amount, md5(
        SECRET_WORD + MERCHANT_ID).hexdigest(), merchant_field_value)
    return md5(s).hexdigest()


def md5sig_generate(obj):
    md5_word = md5(SECRET_WORD).hexdigest().upper()
    s = u"".join((MERCHANT_ID, obj.transaction_id, md5_word,
                  obj.mb_amount, obj.mb_currency, obj.status))
    return md5(s).hexdigest().upper()


def transaction_id_generate():
    tid = "mb_%s" % md5(str(datetime.now()) + str(random())).hexdigest()[:29]
    try:
        MoneybookersTransaction._default_manager.get(transaction_id=tid)
    except Exception:
        return tid
    return transaction_id_generate()
