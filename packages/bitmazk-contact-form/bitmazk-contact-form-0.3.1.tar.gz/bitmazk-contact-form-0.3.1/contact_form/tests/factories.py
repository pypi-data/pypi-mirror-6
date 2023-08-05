"""Factories for the models of the ``contact_form`` app."""
import factory
from django_libs.tests.factories import HvadFactoryMixin

from ..models import ContactFormCategory


class ContactFormCategoryFactory(HvadFactoryMixin, factory.DjangoModelFactory):
    """The Factory for the ``ContactFormCategory`` model."""
    FACTORY_FOR = ContactFormCategory

    slug = factory.Sequence(lambda n: 'slug_{0}'.format(n))
    name = factory.Sequence(lambda n: 'name {0}'.format(n))
