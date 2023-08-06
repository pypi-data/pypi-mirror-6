"""Models for the ``multilingual_initiatives`` app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from django_libs.models_mixins import HvadPublishedManager
from filer.fields.file import FilerFileField
from hvad.models import TranslatableModel, TranslatedFields

from . import settings


class Initiative(TranslatableModel):
    """
    Holds information about an initiative.

    :logo: The image file that contains the logo of the initiative.
    :start_date: When the initiative starts.
    :end_date: When the initiative ends.
    :description: A short description of the initiative.
    :website: URL of the website.
    :phone: The phone number of that initiative. E.g. an information hotline
    :organization: The organization, that is responsible for the initiative.
    :title: The title of the initiative.
    :is_published: If the translation of this initiative is published or not.

    """

    logo = FilerFileField(
        verbose_name=_('Logo'),
        blank=True, null=True,
    )

    start_date = models.DateField(
        verbose_name=_('Start date'),
        blank=True, null=True,
    )

    end_date = models.DateField(
        verbose_name=_('End date'),
        blank=True, null=True,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=160,
        blank=True,
    )

    website = models.URLField(
        verbose_name=_('Website'),
        blank=True,
    )

    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=128,
        blank=True,
    )

    organization = models.ForeignKey(
        'multilingual_orgs.Organization',
        verbose_name=_('Organization'),
        blank=True, null=True,
    )
    translations = TranslatedFields(
        title=models.CharField(
            verbose_name=_('Title'),
            max_length=2000,
        ),
        is_published=models.BooleanField(
            verbose_name=_('Is published'),
            default=False,
        )
    )

    objects = HvadPublishedManager()

    def __unicode__(self):
        return self.safe_translation_getter('title', 'Untranslated initiative')


class InitiativePersonRole(models.Model):
    """
    Intermediary model to connect an initiative to a person from
    django-people.

    :initiative: The initiative the person belongs to.
    :person: The person that belongs to that initiative.
    :role: The role of that person inside the initiative.
    :position: An integer for ordering.

    """

    initiative = models.ForeignKey(
        Initiative,
        verbose_name=_('Initiative'),
    )

    person = models.ForeignKey(
        'people.Person',
        verbose_name=_('Person'),
    )

    role = models.ForeignKey(
        'people.Role',
        verbose_name=_('Role'),
        blank=True, null=True,
    )

    position = models.PositiveIntegerField(
        verbose_name=_('Position'),
        blank=True, null=True,
    )


class InitiativePluginModel(CMSPlugin):
    """
    Model for the ``InitiativePluginModel`` cms plugin.

    :display_type: The way the plugin is displayed. E.g. 'big' or 'small'
    :initiative: The initiative this plugin shows.

    """
    display_type = models.CharField(
        max_length=256,
        choices=settings.DISPLAY_TYPE_CHOICES,
        verbose_name=_('Display type'),
    )

    initiative = models.ForeignKey(
        Initiative,
        verbose_name=_('Initiative'),
    )
