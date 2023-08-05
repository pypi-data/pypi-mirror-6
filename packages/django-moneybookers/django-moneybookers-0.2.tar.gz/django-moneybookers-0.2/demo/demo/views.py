from django.shortcuts import render_to_response, HttpResponse

from moneybookers.forms import MoneybookersStandardForm


def view_with_order(request):
    data_dict = {
        "language": "RU",
        "amount": "0.01",
        "currency": "USD",
        "invoice": "4567",
        "user_id": request.user.id,
        "detail1_description": "Product ID:",
        "detail1_text": "4509334",
        "merchant_field": "new_client",
        "merchant_field_value": "1",
        "user_ipaddress": request.META.get("REMOTE_ADDR", "0.0.0.0"),

        #'hide_login': '1',
        #'payment_methods': 'ACC',
    }

    f = MoneybookersStandardForm(initial=data_dict)
    context = {"form": f}
    return render_to_response("order.html", context)


def canceled(request):
    return HttpResponse('canceled')


def done(request):
    return HttpResponse('done')
