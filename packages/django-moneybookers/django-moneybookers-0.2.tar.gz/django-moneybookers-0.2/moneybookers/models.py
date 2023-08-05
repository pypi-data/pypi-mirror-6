# -*- coding: utf-8 -*-

from django.db import models

from moneybookers.conf import *


class MoneybookersTransaction(models.Model):
    # Transaction IDs
    transaction_id = models.CharField(
        "Internal Transaction ID", db_index=True, max_length=32, unique=True,
        help_text="Reference or identification number provided by the "
                  "Merchant. If no transaction_id is submitted, the "
                  "mb_transaction_id value will be posted in the report")
    mb_transaction_id = models.CharField(
        "Moneybookers Transaction ID", db_index=True, max_length=32,
        blank=True,
        help_text="Moneybookers unique transaction ID for the transfer.")
    session_id = models.CharField(
        max_length=32, blank=True,
        help_text="The Merchant server takes the SESSION_ID cookie "
                  "from the appropriate Set-Cookie HTTP header of the "
                  "response. Using this SESSION_ID value the customer can be "
                  "redirected to https://www.moneybookers.com/app/payment.pl"
                  "?sid=<SESSION_ID>")

    # Merchant Details
    pay_to_email = models.CharField(
        default=PAY_TO_EMAIL, max_length=50, blank=True,
        help_text="Email address of the Merchant's moneybookers.com account.")
    hide_login = models.BooleanField(default=False, blank=True)
    prepare_only = models.BooleanField(default=False, blank=True)
    payment_methods = models.CharField(
        max_length=100, blank=True,
        help_text="A comma-separated list of payment method codes to be "
                  "presented to the customer (GATEWAY_PAYMENT_CODES)")
    rid = models.CharField(
        max_length=100, blank=True,
        help_text="Merchants can pass the unique referral ID or email of the "
                  "affiliate from which the customer is referred. The rid "
                  "value must be included within the actual payment request.")
    ext_ref_id = models.CharField(
        max_length=100, blank=True,
        help_text="Merchants can pass additional identifier in this field "
                  "in order to track affiliates.")

    # Customer Details
    language = models.CharField(
        max_length=2, choices=LANGUAGE_CODE, blank=True)
    title = models.CharField(max_length=4, choices=CUSTOMER_TITLE, blank=True)
    firstname = models.CharField(max_length=20, blank=True)
    lastname = models.CharField(max_length=50, blank=True)
    date_of_birth = models.CharField(max_length=8, blank=True)
    address = models.CharField(max_length=100, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=9, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=3, choices=ISO3166_A3, blank=True)

    # Payment Details
    currency = models.CharField(
        max_length=3, choices=ISO4217, default=CURRENCY_CODE, blank=True)
    amount = models.CharField(max_length=20, blank=True)
    amount2 = models.DecimalField(
        max_digits=19, decimal_places=2, default=0, blank=True, null=True)
    amount2_description = models.CharField(max_length=240, blank=True)
    amount3 = models.DecimalField(
        max_digits=19, decimal_places=2, default=0, blank=True, null=True)
    amount3_description = models.CharField(max_length=240, blank=True)
    amount4 = models.DecimalField(
        max_digits=19, decimal_places=2, default=0, blank=True, null=True)
    amount4_description = models.CharField(max_length=240, blank=True)
    detail1_description = models.CharField(max_length=240, blank=True)
    detail1_text = models.CharField(max_length=240, blank=True)
    detail2_description = models.CharField(max_length=240, blank=True)
    detail2_text = models.CharField(max_length=240, blank=True)
    detail3_description = models.CharField(max_length=240, blank=True)
    detail3_text = models.CharField(max_length=240, blank=True)
    detail4_description = models.CharField(max_length=240, blank=True)
    detail4_text = models.CharField(max_length=240, blank=True)
    detail5_description = models.CharField(max_length=240, blank=True)
    detail5_text = models.CharField(max_length=240, blank=True)

    # Status report from Moneybookers to Merchant
    pay_from_email = models.CharField(max_length=50, blank=True)
    customer_id = models.CharField(
        max_length=9, blank=True,
        help_text="Unique ID for the customer's moneybookers.com account. "
                  "To receive the customer_id value, please contact your "
                  "account manager or merchantservices@moneybookers.com")
    mb_amount = models.CharField(max_length=20, blank=True)
    mb_currency = models.CharField(max_length=3, choices=ISO4217, blank=True)

    # By default NULL = Only click/generate of form and redirect
    # customer to moneybookers
    status = models.CharField(
        max_length=2, blank=True,
        choices=TRANSACTION_STATUS)
    failed_reason_code = models.CharField(
        max_length=2, choices=FAILED_REASON_CODES, blank=True,
        help_text="To receive the failed_reason_code value, please contact "
                  "your account manager or merchantservices@moneybookers.com")
    md5sig = models.CharField(max_length=32, blank=True)
    payment_type = models.CharField(
        max_length=5, blank=True, choices=GATEWAY_PAYMENT_CODES,
        help_text="The payment instrument used by the customer "
                  "on the Gateway.")
    merchant_field = models.CharField(max_length=342, blank=True)

    # Non-Moneybookers Variables
    user_ipaddress = models.IPAddressField(default="0.0.0.0", blank=True)
    mb_ipaddress = models.IPAddressField(default="0.0.0.0", blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user_id = models.IntegerField(
        db_index=True, blank=True, null=True, help_text="Merchant's customer")
    invoice = models.CharField(
        max_length=32, db_index=True, blank=True,
        help_text="Merchant's custom field as invoice/order identification")
    md5merchant = models.CharField(
        max_length=32, blank=True,
        help_text="Field to check that user_id, invoice and amount are true. "
                  "mb_amount with mb_currency are checked in md5sig")
    error = models.BooleanField(default=False)
    error_text = models.TextField(blank=True)

    def __unicode__(self):
        return u"<Transaction: %s>" % self.transaction_id

    class Meta:
        db_table = "moneybookers_transaction"
        verbose_name = "Moneybookers Transaction"
        verbose_name_plural = "Moneybookers Transactions"

    def set_error(self, text):
        self.error = True
        self.error_text += "%s; " % text
