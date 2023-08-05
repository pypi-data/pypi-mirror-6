import stripe
from datetime import date

from django import forms
from django.conf import settings
from django.db import models
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.shortcuts import redirect
from django.utils.timezone import now as tz_now
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.fields import RichTextField
from mezzanine.core.models import RichText
from mezzanine.pages.models import Page
from mezzanine.pages.page_processors import processor_for

from localflavor.us.forms import USPhoneNumberField

from mezzanine_donate.forms import MonthYearWidget

stripe.api_key = settings.STRIPE_API_KEY


class DonationForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    phone = USPhoneNumberField()
    amount = forms.DecimalField()
    note = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)


class Donation(models.Model):
    donation_page = models.ForeignKey('DonationPage')
    donated_at = models.DateTimeField(default=tz_now)
    charge_id = models.CharField(max_length=32)
    name = models.CharField(max_length=256)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    note = models.TextField()

    def charge(self, card_token, description):
        if self.charge_id:
            raise RuntimeError('Tried to make the same charge twice')

        price_in_cents = (self.amount * 100).to_integral_value()
        try:
            response = stripe.Charge.create(
                amount=int(price_in_cents),
                currency="usd",
                card=card_token,
                description=description
            )
        except stripe.CardError:
            raise

        self.charge_id = response.id

    def __unicode__(self):
        return "Donation of ${0} from {1}".format(
            self.amount, self.email
        )


class DonationPage(Page, RichText):
    """
    A user-built form.
    """
    charge_description = models.CharField(
        max_length=256,
        help_text=_("A short description to be displayed on the Email "
                    "receipt sent to the user."))
    response = RichTextField(_("Response"))
    send_email = models.BooleanField(_("Send email to user"), default=True,
        help_text=_("To send an email to the email address supplied in "
                    "the form upon submission, check this box."))
    email_from = models.EmailField(_("From address"), blank=True,
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send email to others"), blank=True,
        help_text=_("Provide a comma separated list of email addresses "
                    "to be notified upon form submission. Leave blank to "
                    "disable notifications."),
        max_length=200)
    email_subject = models.CharField(_("Subject"), max_length=200, blank=True)
    email_message = models.TextField(_("Message"), blank=True,
        help_text=_("Emails sent based on the above options will contain "
                    "each of the form fields entered. You can also enter "
                    "a message here that will be included in the email."))

    class Meta:
        verbose_name = _("Donation Page")
        verbose_name_plural = _("Donation Pages")


@processor_for(DonationPage)
def donation_form(request, page):
    form = DonationForm()
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            token = request.POST['stripeToken']
            donation = Donation(
                donation_page=page.donationpage,
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                amount=form.cleaned_data['amount'],
                note=form.cleaned_data['note']
            )
            try:
                donation.charge(token, page.donationpage.charge_description)
            except stripe.CardError as e:
                errors = form._errors.setdefault(NON_FIELD_ERRORS, ErrorList())
                errors.append(e.message)
            else:
                donation.save()
                url = page.get_absolute_url() + "?sent=1"
                return redirect(url)
    return {"form": form}
