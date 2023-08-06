"""Factories for the cmsplugin_accordion app."""
import factory

from .. import models


class AccordionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Accordion

    name = factory.Sequence(lambda n: 'name {0}'.format(n))


class AccordionRowFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.AccordionRow

    accordion = factory.SubFactory(AccordionFactory)
    title = factory.Sequence(lambda n: 'title {0}'.format(n))


class AccordionPluginModel(factory.DjangoModelFactory):
    FACTORY_FOR = models.AccordionPluginModel

    accordion = factory.SubFactory(AccordionFactory)
