from django import forms
from django.utils.translation import ugettext_lazy as _
from lxml.html.soupparser import fromstring
from djinn_contenttypes.forms.base import BaseSharingForm
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from djinn_announcements.settings import SERVICEANNOUNCEMENT_STATUS_VOCAB, \
    ANNOUNCEMENT_PRIORITY_VOCAB


class ServiceAnnouncementForm(BaseSharingForm):

    # Translators: serviceannouncement edit general help
    help = _("Edit serviceannouncement")

    text = forms.CharField(label=_("Description"),
                           help_text="Maximaal 300 karakters",
                           max_length=300,
                           widget=forms.Textarea()
    )

    start_date = forms.DateTimeField(
        label=_("Start date"),
        widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
            )
        )

    end_date = forms.DateTimeField(
        label=_("(Expected) end date"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
            )
        )

    status = forms.IntegerField(
        label=_("Status"),
        required=False,
        initial=-1,
        widget=forms.Select(
            choices=SERVICEANNOUNCEMENT_STATUS_VOCAB)
        )

    priority = forms.IntegerField(
        label=_("Priority"),
        initial=0,
        widget=forms.Select(
            choices=ANNOUNCEMENT_PRIORITY_VOCAB)
        )

    #link = forms.URLField(
    #   label=_("Link")
    #    )

    def __init__(self, *args, **kwargs):

        super(ServiceAnnouncementForm, self).__init__(*args, **kwargs)

        self.fields['title'].max_length = 100

        self.init_relation_fields()
        self.init_share_fields()
        self.fields['owner'].initial = kwargs['user'].profile

    def save(self, commit=True):

        res = super(ServiceAnnouncementForm, self).save(commit=commit)
        self.save_relations(commit=commit)
        self.save_shares(commit=commit)

        return res

    class Meta(BaseSharingForm.Meta):
        model = ServiceAnnouncement
