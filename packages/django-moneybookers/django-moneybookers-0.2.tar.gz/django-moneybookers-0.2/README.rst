Django-Moneybookers
===================
`Moneyboookers <http://www.moneybookers.com/>`_ gateway for `Django <http://www.djangoproject.com/>`_ with two payment forms: common and secure.


Moneyboookers gateway allows you to accept payments on your website. It contains two payment paths:

* Form genaration with POST to Moneybookers
* Secure redirect with prepared SESSION_ID

In both cases additional security checks are implemented.

Full API documentation: "Moneybookers Payment Gateway"


How to install
--------------
1. Download the source and place in your apps folder

2. Edit "settings.py"
    - add "moneybookers" to your "INSTALLED_APPS"
    - add following settings (example):

.. code-block:: python

    MONEYBOOKERS_MERCHANT_ID = "123456"
    MONEYBOOKERS_SECRET_WORD = "YourSecretWord"
    MONEYBOOKERS_PAY_TO_EMAIL = "billing@mycompany.com"
    MONEYBOOKERS_STATUS_URL = "https://www.mycompany.com/moneybookers/status_url/"
    MONEYBOOKERS_CURRENCY_CODE = "EUR"

not required, but recommended:

.. code-block:: python

    MONEYBOOKERS_CANCEL_URL = "https://www.mycompany.com/moneybookers/cancel/"
    MONEYBOOKERS_RETURN_URL = "https://www.mycompany.com/moneybookers/ok/"
    MONEYBOOKERS_STATUS_URL2 = "mailto: billing@mycompany.com"
    MONEYBOOKERS_RECEPIENT_DESCRIPTION = "My Company Limited"
    
For more optional settings please see "conf.py"
    
    
3. Add to "urls.py" paths

.. code-block:: python

    urlpatterns = patterns('',
        (r'^moneybookers/status_url/', include('moneybookers.urls')),
        (r'^moneybookers/cancel/', 'MoneybookersCancel'),
        (r'^moneybookers/ok/', 'MoneybookersOk'),
        (r'^order/$', 'View_With_Order'),
    )
    
    
4. Create table in your database

.. code-block:: bash

    manage.py syncdb

    
5. Create/render form

* Common way:

Create an instance of the form in your "views.py" and make render in your template

.. code-block:: python

    from moneybookers.forms import MoneybookersStandardForm

    def View_With_Order(request):
        mb_dict = {
          "amount":"25.00",
          "invoice":"4567",
          "user_id": request.user.id,
          "detail1_description":"Product ID:",
          "detail1_text":"4509334",
          "merchant_field": "new_client",
          "merchant_field_value": "1",
          "user_ipaddress": request.META.get("REMOTE_ADDR", "0.0.0.0")
        }
        f = MoneybookersStandardForm(initial=mb_dict)
        context = {"form": f}
        return render_to_response("order.html", context)
    
In "order.html":

.. code-block:: html

    <h1>Pay with Moneybookers now!</h1>
    {{ form.render }}
    
    
After payment Moneybookers sends a signal to your server (status_url). The transaction will be saved in the database, then will be send a signal MoneybookersSignal. You can use it to process your own actions (add amount to users account, etc..). An example to use in "models.py":
from moneybookers.signals import moneybookers_signal
from django.db import transaction
from django.core.mail import mail_admins

.. code-block:: python

    @transaction.commit_manually
    def MoneybookersSignal(sender, **kwargs):
            if sender.error:
                    mail_admins("Moneybookers: bad transaction %s" % sender.transaction_id, sender.error_text)
                    return
            sid = transaction.savepoint()
            try:
                    user = User.objects.get(id=sender.user_id)
                    profile = user.get_profile()
                    profile.money = profile.money + sender.amount
                    profile.save()
                    mail_admins( "Moneybookers: good transaction %s" % sender.transaction_id, "%s added to user %s" % (sender.amount, sender.user_id) )
                    transaction.savepoint_commit(sid)
                except Exception, e:
                    transaction.savepoint_rollback(sid)
                    mail_admins("Moneybookers: database rollback: transaction %s" % sender.transaction_id, e)
                transaction.commit()

    moneybookers_signal.connect(MoneybookersSignal, dispatch_uid="yourapp.models.MoneybookersSignal")
    
    
Secure way:

Add to "urls.py" another path

.. code-block:: python

    urlpatterns = patterns('',
        (r'^moneybookers_redirect/$', 'payment_moneybookers_redirect'),
    )
    
Create an form in your template yourself with POST-Url to "moneybookers_redirect"

.. code-block:: html

    <form action="https://www.mycompany.com/moneybookers_redirect/" method="post">
        <input name="invoice" value="777" type="hidden">
        <input type="submit" value="Pay with Moneybookers"/>
    </form>

In your "views.py" you must check the invoice number

.. code-block:: python

    from django.contrib.auth.decorators import login_required
    from django.views.decorators.http import require_POST
    from django.http import HttpResponseRedirect, HttpResponseServerError
    
    @login_required
    @require_POST
    def payment_moneybookers_redirect(request):
        invoice = request.POST.get("invoice", None)
        mb_dict = {
            "language": "EN",
            "country": ...,
            "amount": ...,
            "prepare_only": True,
            "detail1_description": "Invoice #",
            "detail1_text": invoice,
            "invoice": invoice,
            "user_id": request.user.id,
            "user_ipaddress": request.META.get("REMOTE_ADDR", "0.0.0.0")
            }
    
        # If you want accept only credit cards without user to register on moneybookers:
        mb_dict["hide_login"] = "1"
        mb_dict["payment_methods"] = "ACC"
    
        f = MoneybookersSecureForm(initial=mb_dict)
        url = f.redirect_url()
        if url:
            return HttpResponseRedirect(url)
        return HttpResponseServerError()
    Patch your "models.py" with signal MoneybookersSignal like in "common way"


Based on "Moneybookers Payment Gateway Merchant Integration Manual" v6.10 / 8 Nov. 2010

Alex Aster, www.alrond.com, 2010
FreeBSD License
