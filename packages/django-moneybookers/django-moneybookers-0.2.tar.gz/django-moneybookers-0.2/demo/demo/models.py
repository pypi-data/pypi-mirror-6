from pprint import pprint

from django.forms.models import model_to_dict
from django.core.mail import mail_admins
from django.db import transaction

from moneybookers.signals import moneybookers_signal
from django.contrib.auth.models import User


@transaction.commit_manually
def MoneybookersSignal(sender, **kwargs):
    pprint(model_to_dict(sender))

    if sender.error:
        mail_admins(
            "Moneybookers: bad transaction %s" % sender.transaction_id,
            sender.error_text)
        return
    sid = transaction.savepoint()
    try:
        user = User.objects.get(id=sender.user_id)
        profile = user.get_profile()
        profile.money = profile.money + sender.amount
        profile.save()
        mail_admins(
            "Moneybookers: good transaction %s" % sender.transaction_id,
            "%s added to user %s" % (sender.amount, sender.user_id))
        transaction.savepoint_commit(sid)
    except Exception, e:
        transaction.savepoint_rollback(sid)
        t_id = sender.transaction_id
        mail_admins(
            "Moneybookers: database rollback: transaction %s" % t_id, e)
    transaction.commit()


moneybookers_signal.connect(
    MoneybookersSignal, dispatch_uid="yourapp.models.MoneybookersSignal")
