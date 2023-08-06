"""Factories for the ``multilingual_orgs`` app."""
import factory

from django_libs.tests.factories import HvadFactoryMixin
from people.tests.factories import PersonFactory

from ..models import (
    Organization,
    OrganizationPluginModel,
    OrganizationPersonRole,
)


class OrganizationFactory(HvadFactoryMixin, factory.DjangoModelFactory):
    """Factory for the ``Organization`` model."""
    FACTORY_FOR = Organization

    title = factory.Sequence(lambda n: 'my org title {0}'.format(n))


class OrganizationPersonRoleFactory(factory.DjangoModelFactory):
    """Factory for the ``OrganizationPersonRole`` model."""
    FACTORY_FOR = OrganizationPersonRole

    organization = factory.SubFactory(OrganizationFactory)
    person = factory.SubFactory(PersonFactory)


class OrganizationPluginModelFactory(factory.DjangoModelFactory):
    """Factory for ``OrganizationPluginModel`` objects."""
    FACTORY_FOR = OrganizationPluginModel

    display_type = 'small'
    organization = factory.SubFactory(OrganizationFactory)
