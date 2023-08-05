# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from moneybookers.models import MoneybookersTransaction
from moneybookers.forms import MoneybookersStatusForm
from moneybookers.conf import PAY_TO_EMAIL, STATUS_URL
from moneybookers.utils import md5merchant_generate, md5sig_generate
from moneybookers.signals import moneybookers_signal


@require_POST
@csrf_exempt
def status(request):
    status_data = None
    error = None
    mb = None
    user_id_old = None
    invoice_old = None
    amount_old = None
    if request.POST.has_key("transaction_id"):
        try:
            mb = MoneybookersTransaction.objects.get(
                transaction_id=request.POST["transaction_id"])
            user_id_old = mb.user_id
            invoice_old = mb.invoice
            amount_old = mb.amount
        except MoneybookersTransaction.DoesNotExist:
            pass
    form = MoneybookersStatusForm(request.POST, instance=mb)
    if form.is_valid():
        try:
            status_data = form.save(commit=False)
        except Exception, e:
            error = "Exception: %s" % e
    else:
        error = "Invalid form: %s" % form.errors
    if not status_data:
        status_data = MoneybookersTransaction()

    if status_data.md5sig != md5sig_generate(status_data):
        return HttpResponseForbidden("Allowed only for Moneybookers")

    if error:
        status_data.set_error(error)

    status_data.mb_ipaddress = request.META.get("REMOTE_ADDR", "0.0.0.0")

    if not request.is_secure() and STATUS_URL[:5] == "https":
        status_data.set_error("Moneybookers request was not SSL-encrypted")

    merchant_field = status_data.merchant_field
    merchant_value = request.POST.get(merchant_field, "")

    if status_data.md5merchant != md5merchant_generate(
            status_data.user_id, status_data.invoice,
            status_data.amount, merchant_value):
        status_data.set_error("Invalid md5 of merchants fields")

    if user_id_old and user_id_old != status_data.user_id:
        status_data.set_error("Wrong User ID: old=%s, new=%s" % (
            user_id_old, status_data.user_id))

    if invoice_old and invoice_old != status_data.invoice:
        status_data.set_error("Wrong Order ID: old=%s, new=%s" % (
            invoice_old, status_data.invoice))

    if amount_old and amount_old != status_data.mb_amount:
        status_data.set_error("Wrong amount: amount=%s, mb_amount=%s" % (
            amount_old, status_data.amount))

    if status_data.status != "2":
        status_data.set_error(
            """Payment status is not "Processed": %s""" % status_data.status)

    if status_data.pay_to_email != PAY_TO_EMAIL:
        status_data.set_error(
            "Invalid merchant's email: %s" % status_data.pay_to_email)

    # Save model and send signal
    status_data.merchant_field = u"%s=%s" % (merchant_field, merchant_value)
    status_data.save()
    status_data.__dict__[merchant_field] = merchant_value
    moneybookers_signal.send(sender=status_data)

    return HttpResponse("OK")
