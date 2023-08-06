"""Factories for the ``multilingual_initiatives`` app."""
import factory

from django_libs.tests.factories import HvadFactoryMixin
from people.tests.factories import PersonFactory

from ..models import (
    Initiative,
    InitiativePersonRole,
    InitiativePluginModel,
)


class InitiativeFactory(HvadFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``Initiative`` model."""
    FACTORY_FOR = Initiative

    title = factory.Sequence(lambda n: 'my initiative title {0}'.format(n))


class InitiativePersonRoleFactory(factory.DjangoModelFactory):
    """Factory for the ``InitiativePersonRole`` model."""
    FACTORY_FOR = InitiativePersonRole

    initiative = factory.SubFactory(InitiativeFactory)
    person = factory.SubFactory(PersonFactory)


class InitiativePluginModelFactory(factory.DjangoModelFactory):
    """Factory for ``InitiativePluginModel`` objects."""
    FACTORY_FOR = InitiativePluginModel

    display_type = 'small'
    initiative = factory.SubFactory(InitiativeFactory)
