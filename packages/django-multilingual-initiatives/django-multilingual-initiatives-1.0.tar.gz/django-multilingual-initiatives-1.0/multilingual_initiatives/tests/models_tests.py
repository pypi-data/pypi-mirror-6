"""Tests for the models of the ``multilingual_initiatives`` app."""
from mock import Mock

from django.test import TestCase
from people.tests.factories import PersonFactory

from ..models import Initiative
from .factories import (
    InitiativeFactory,
    InitiativePersonRoleFactory,
    InitiativePluginModelFactory,
)


class InitiativeTestCase(TestCase):
    """Tests for the ``Initiative`` model."""
    longMessage = True

    def test_model(self):
        obj = InitiativeFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class InitiativePersonRoleTestCase(TestCase):
    """Tests for the ``InitiativePersonRole`` model."""
    longMessage = True

    def test_model(self):
        person = PersonFactory(language_code='en')
        obj = InitiativePersonRoleFactory(person=person)
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class InitiativePluginModelTestCase(TestCase):
    """Tests for the ``InitiativePluginModel`` model."""
    longMessage = True

    def test_model(self):
        obj = InitiativePluginModelFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
