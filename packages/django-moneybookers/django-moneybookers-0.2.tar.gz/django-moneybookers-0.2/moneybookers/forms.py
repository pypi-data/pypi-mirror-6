# -*- coding: utf-8 -*-
import httplib
import urllib
import re

from django.utils.safestring import mark_safe
from django import forms

from moneybookers.utils import md5merchant_generate, transaction_id_generate
from moneybookers.models import MoneybookersTransaction
from moneybookers.fields import ExistHiddenInput
from moneybookers import validators
from moneybookers.conf import *


class MoneybookersStatusForm(forms.ModelForm):
    class Meta:
        model = MoneybookersTransaction
        exclude = ('user_ipaddress', 'mb_ipaddress')


class MoneybookersStandardForm(forms.Form):
    pay_to_email = forms.CharField(
        max_length=50, widget=forms.HiddenInput(), initial=PAY_TO_EMAIL)
    recipient_description = forms.CharField(
        max_length=30, widget=ExistHiddenInput(), required=False,
        initial=RECEPIENT_DESCRIPTION)
    transaction_id = forms.CharField(
        max_length=32, widget=ExistHiddenInput(), required=False)
    return_url = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False,
        initial=RETURN_URL)
    return_url_text = forms.CharField(
        max_length=35, widget=ExistHiddenInput(), required=False,
        initial=RETURN_URL_TEXT)
    return_url_target = forms.CharField(
        max_length=1, widget=ExistHiddenInput(), required=False,
        validators=[validators.url_target]) # choices=URL_TARGET
    cancel_url = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False,
        initial=CANCEL_URL)
    cancel_url_target = forms.CharField(
        max_length=1, widget=ExistHiddenInput(), required=False,
        validators=[validators.url_target]) # choices=URL_TARGET
    status_url = forms.CharField(
        max_length=400, widget=forms.HiddenInput(), initial=STATUS_URL)
    status_url2 = forms.CharField(
        max_length=400, widget=ExistHiddenInput(), required=False,
        initial=STATUS_URL2)
    new_window_redirect = forms.NullBooleanField(
        required=False, widget=ExistHiddenInput())
    language = forms.CharField(
        max_length=2, widget=forms.HiddenInput(),
        validators=[validators.language_code], initial=LANGUAGE_CODE[0][0])
    hide_login = forms.NullBooleanField(
        required=False, widget=ExistHiddenInput())
    confirmation_note = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    logo_url = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False,
        initial=LOGO_URL)
    prepare_only = forms.NullBooleanField(
        required=False, widget=ExistHiddenInput())
    rid = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)
    ext_ref_id = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)

    # Customer Details
    pay_from_email = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)
    title = forms.CharField(
        max_length=4, widget=ExistHiddenInput(),
        validators=[validators.customer_title], required=False)
    firstname = forms.CharField(
        max_length=20, widget=ExistHiddenInput(), required=False)
    lastname = forms.CharField(
        max_length=50, widget=ExistHiddenInput(), required=False)
    date_of_birth = forms.CharField(
        max_length=8, widget=ExistHiddenInput(), min_length=8, required=False)
    address = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)
    address2 = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)
    phone_number = forms.CharField(
        max_length=20, widget=ExistHiddenInput(), required=False)
    postal_code = forms.CharField(
        max_length=9, widget=ExistHiddenInput(), required=False)
    city = forms.CharField(
        max_length=50, widget=ExistHiddenInput(), required=False)
    state = forms.CharField(
        max_length=50, widget=ExistHiddenInput(), required=False)
    country = forms.CharField(
        max_length=3, widget=ExistHiddenInput(),
        validators=[validators.country_code], required=False)

    # Payment Details
    payment_methods = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)
    currency = forms.CharField(
        max_length=3, widget=forms.HiddenInput(),
        validators=[validators.valuta_code], initial=ISO4217[0][0])
    amount = forms.CharField(
        max_length=20, widget=forms.HiddenInput())
    amount2 = forms.DecimalField(
        max_digits=19, decimal_places=2, required=False,
        widget=ExistHiddenInput())
    amount2_description = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    amount3 = forms.DecimalField(
        max_digits=19, decimal_places=2, widget=ExistHiddenInput(),
        required=False)
    amount3_description = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    amount4 = forms.DecimalField(
        max_digits=19, decimal_places=2, widget=ExistHiddenInput(),
        required=False)
    amount4_description = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail1_description = forms.CharField(
        max_length=240, widget=forms.HiddenInput())
    detail1_text = forms.CharField(
        max_length=240, widget=forms.HiddenInput())
    detail2_description = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail2_text = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail3_description = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail3_text = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail4_description = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail4_text = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    detail5_description = forms.CharField(max_length=240,
                                          widget=ExistHiddenInput(),
                                          required=False)
    detail5_text = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)

    merchant_fields = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    user_id = forms.CharField(
        max_length=10, widget=ExistHiddenInput(), required=False)
    invoice = forms.CharField(
        max_length=32, widget=ExistHiddenInput(), required=False)
    merchant_field = forms.CharField(
        max_length=100, widget=ExistHiddenInput(), required=False)
    merchant_field_value = forms.CharField(
        max_length=240, widget=ExistHiddenInput(), required=False)
    md5merchant = forms.CharField(
        max_length=32, widget=ExistHiddenInput(), required=False)
    user_ipaddress = forms.IPAddressField(
        widget=ExistHiddenInput(), required=False)
    session_id = forms.CharField(
        max_length=32, widget=ExistHiddenInput(), required=False)

    def __init__(self, prepare_transaction=False, button_image_url=None,
                 button_text=None, test=False, *args, **kwargs):
        super(MoneybookersStandardForm, self).__init__(*args, **kwargs)
        self.test = test
        self.prepare_transaction = prepare_transaction
        if prepare_transaction:
            self.set_value("transaction_id", transaction_id_generate())
        self.button_image_url = BUTTON_IMAGE_URL
        if button_image_url:
            self.button_image_url = button_image_url
        self.button_text = "Pay via Moneybookers"
        if button_text:
            self.button_text = button_text
        self.model = None

    def get_value(self, name):
        return self.initial.get(name, self.fields[name].initial)

    def set_value(self, name, value):
        if not value:
            self.initial[name] = None
        else:
            self.initial[name] = value

    def list_merchant_fields(self):
        mf = []
        if self.get_value("user_id"):
            mf.append("user_id")
        if self.get_value("invoice"):
            mf.append("invoice")
        if self.get_value("merchant_field"):
            merchant_field = re.sub(re.compile('\W'), '',
                                    self.get_value("merchant_field"))
            self.set_value("merchant_field", merchant_field)
            mf.append(merchant_field)
            mf.append("merchant_field")
        if mf:
            mf.append("md5merchant")
        return u",".join(mf)

    def render(self):
        return mark_safe(
            u"""
            <form action="%s" method="post">
            %s %s</form>""" % (self.post_action(),
                               self.render_as_p(), self.render_button()))

    def post_action(self):
        return mark_safe(
            u"%s" % {False: GATEWAY, True: TEST_GATEWAY, }[self.test])

    def merchant_fields_generate(self):
        mf = self.list_merchant_fields()
        self.set_value("merchant_fields", mf)
        if mf:
            self.set_value("md5merchant", md5merchant_generate(
                self.get_value("user_id"), self.get_value("invoice"),
                self.get_value("amount"),
                self.get_value("merchant_field_value")))
        cf = u""
        merchant_field = self.get_value("merchant_field")
        merchant_field_value = self.get_value("merchant_field_value")
        if self.prepare_transaction:
            self.model_create()
            self.model_save()
        if merchant_field:
            cf += u"""<input type="hidden" name="%s" value="%s">""" % (
                merchant_field, merchant_field_value)
            self.set_value("merchant_field_value", None)
        return mark_safe(u"%s" % cf)

    def render_as_p(self):
        return mark_safe(
            u"%s %s" % (self.merchant_fields_generate(), self.as_p()))

    def render_as_ul(self):
        return mark_safe(
            u"%s %s" % (self.merchant_fields_generate(), self.as_ul()))

    def render_as_table(self):
        return mark_safe(
            u"%s %s" % (self.merchant_fields_generate(), self.as_table()))

    def render_button(self):
        if self.button_image_url:
            return mark_safe(
                u"""<input type="image" src="%s" name="submit" alt="%s"
                border="0" />""" % (self.button_image_url, self.button_text))
        return mark_safe(
            u"""<input type="submit" value="%s"/>""" % self.button_text)

    def model_create(self):
        m = MoneybookersTransaction()
        fields = ["transaction_id", "session_id", "hide_login", "prepare_only",
                  "payment_methods", "rid", "ext_ref_id", "language", "title",
                  "firstname", "lastname", "date_of_birth", "address",
                  "address2",
                  "phone_number", "postal_code", "city", "state", "country",
                  "currency", "amount", "amount2", "amount2_description",
                  "amount3", "amount3_description", "amount4",
                  "amount4_description", "detail1_description", "detail1_text",
                  "detail2_description", "detail2_text", "detail3_description",
                  "detail3_text", "detail4_description", "detail4_text",
                  "detail5_description", "detail5_text", "merchant_field",
                  "user_ipaddress", "user_id", "invoice", "md5merchant",
                  "merchant_field_value"]
        for f in fields:
            value = self.get_value(f)
            if value:
                if f == "merchant_field_value":
                    value = "%s=%s" % (m.merchant_field, value)
                    f = "merchant_field"
                m.__dict__[f] = value
        self.set_value("user_ipaddress", None)
        self.model = m

    def model_save(self, name=None, value=None):
        if name:
            self.model.__dict__[name] = value
        self.model.save()


class MoneybookersSecureForm(MoneybookersStandardForm):
    def __init__(self, test=False, *args, **kwargs):
        super(MoneybookersStandardForm, self).__init__(*args, **kwargs)
        self.test = test
        self.prepare_transaction = True
        self.set_value("prepare_only", True)
        self.set_value("transaction_id", transaction_id_generate())
        self.model = None

    def _extract_cookie(self, header, name):
        name = name + "="
        start = header.find(name)
        end = header.find(";", start + len(name))
        if start > -1 and end > -1 and end > start:
            return header[start + len(name):end]
        return ""

    def _get_session_id(self):
        sid = None
        self.merchant_fields_generate()
        values = {
            'name': 'Michael Foord',
            'location': 'Northampton',
            'language': 'Python'
        }
        data = urllib.urlencode(values)
        uri = {False: GATEWAY_URI, True: TEST_GATEWAY_URI, }[self.test]
        try:
            mb_conn = httplib.HTTPSConnection(GATEWAY_HOST)
            mb_conn.connect()
            mb_conn.putrequest("POST", uri)
            mb_conn.putheader("Connection", "keep-alive")
            mb_conn.putheader("User-Agent", USER_AGENT)
            mb_conn.putheader("Accept", "text/html")
            mb_conn.putheader(
                "Content-Type", "application/x-www-form-urlencoded")
            mb_conn.putheader("Content-Length", str(len(data)))
            mb_conn.endheaders()
            mb_conn.send(data)
            response = mb_conn.getresponse()
            if response.status == 200:
                cookie = response.msg.getheader("Set-Cookie")
                sid = self._extract_cookie(cookie, "SESSION_ID")
                self.model_save("session_id", sid)
            mb_conn.close()
        except Exception:
            pass
        return sid

    def redirect_url(self):
        sid = self._get_session_id()
        if sid:
            return "%s?sid=%s" % (GATEWAY, sid)