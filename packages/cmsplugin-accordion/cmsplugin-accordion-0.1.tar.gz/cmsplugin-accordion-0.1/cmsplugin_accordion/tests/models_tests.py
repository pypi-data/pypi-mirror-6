"""Tests for the models of the cmsplugin_accordion app."""
from django.test import TestCase

from . import factories


class AccordionTestCase(TestCase):
    """Tests for the ``Accordion`` model class."""
    def test_model(self):
        obj = factories.AccordionFactory()
        self.assertTrue(obj.pk)


class AccordionRowTestCase(TestCase):
    """Tests for the ``AccordionRow`` model class."""
    def test_model(self):
        obj = factories.AccordionRowFactory()
        self.assertTrue(obj.pk)


class AccordionPluginModelTestCase(TestCase):
    """Tests for the ``AccordionPluginModel`` model class."""
    def test_model(self):
        obj = factories.AccordionPluginModel()
        self.assertTrue(obj.pk)
