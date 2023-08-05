from django.conf.urls import patterns, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from mezzanine.utils.urls import admin_url

from .models import DonationPage, Donation

try:
    from mezzanine_slides.models import Slide
except ImportError:
    SlideInline = None
else:
    class SlideInline(TabularDynamicInlineAdmin):
        model = Slide

class DonationPageAdmin(PageAdmin):
    inlines = (SlideInline,)

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super(DonationPageAdmin, self).get_urls()
        extra_urls = patterns("",
            url("^(?P<form_id>\d+)/donations/$",
                self.admin_site.admin_view(self.donations_view),
                name="donation_entries"),
        )
        return extra_urls + urls

    def donations_view(self, request, form_id):
        """
        Displays the list of donations related to the given donation page.
        """
        if request.POST.get("back"):
            change_url = admin_url(DonationPage, "change", form_id)
            return HttpResponseRedirect(change_url)

        donations = Donation.objects.filter(donation_page_id=form_id)
        template = "admin/mezzanine_donate/donations.html"
        context = {"title": "View Donations", 'donations': donations}
        return render_to_response(template, context, RequestContext(request))


class RichTextPageAdmin(PageAdmin):
    inlines = (SlideInline,)

admin.site.register(DonationPage, DonationPageAdmin)
