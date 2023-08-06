"""Tests for the models of the ``multilingual_orgs`` app."""
from django.test import TestCase

from people.tests.factories import PersonFactory

from .factories import (
    OrganizationFactory,
    OrganizationPersonRoleFactory,
    OrganizationPluginModelFactory,
)


class OrganizationTestCase(TestCase):
    """Tests for the ``Organization`` model."""
    longMessage = True

    def test_model(self):
        obj = OrganizationFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class OrganizationPersonRoleTestCase(TestCase):
    """Tests for the ``OrganizationPersonRole`` model."""
    longMessage = True

    def test_model(self):
        # TODO somehow without language_code it doesn't work.
        person = PersonFactory(language_code='en')
        obj = OrganizationPersonRoleFactory(person=person)
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))


class OrganizationPluginModelTestCase(TestCase):
    """Tests for the ``OrganizationPluginModel`` model."""
    longMessage = True

    def test_model(self):
        obj = OrganizationPluginModelFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to instantiate and save the model.'))
