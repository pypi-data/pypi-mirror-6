# -*- coding: utf-8 -*-
from django.contrib import admin

from moneybookers.models import MoneybookersTransaction


class MoneybookersTransactionAdmin(admin.ModelAdmin):
    readonly_fields = ("create_date", "update_date")
    fieldsets = (
        (None, {
            "fields": (
                "transaction_id", "mb_transaction_id", "user_id", "invoice",
                "mb_amount",
                "status", "create_date", "update_date", "error")
        }),
        ("Customer Details", {
            'classes': ('collapse',),
            "fields": (
                "session_id", "pay_from_email", "language", "title",
                "firstname",
                "lastname", "date_of_birth", "address", "address2",
                "phone_number",
                "postal_code", "city", "state", "country", "customer_id")
        }),
        ("Payment Details", {
            'classes': ('collapse',),
            "fields": (
                "currency", "mb_currency", "payment_methods", "payment_type",
                "amount",
                "amount2", "amount2_description", "amount3",
                "amount3_description",
                "amount4", "amount4_description", "detail1_description",
                "detail1_text",
                "detail2_description", "detail2_text", "detail3_description",
                "detail3_text", "detail4_description", "detail4_text",
                "detail5_description", "detail5_text")
        }),
        ("Merchant Details", {
            'classes': ('collapse',),
            "fields": ("pay_to_email", "rid", "ext_ref_id", "merchant_field")
        }),
        ("Technical details", {
            "classes": ("collapse",),
            "fields": (
                "error_text", "failed_reason_code", "md5sig", "hide_login",
                "prepare_only",
                "user_ipaddress", "mb_ipaddress", "md5merchant")
        }),
    )
    list_display = (
        "__unicode__", "user_id", "invoice", "mb_amount", "payment_type",
        "status",
        "create_date", "update_date")
    list_filter = (
        "error", "status", "create_date", "update_date", "payment_type",
        "hide_login", "prepare_only", "rid")
    date_hierarchy = 'create_date'
    search_fields = (
        "transaction_id", "mb_transaction_id", "user_id", "invoice")


admin.site.register(MoneybookersTransaction, MoneybookersTransactionAdmin)
