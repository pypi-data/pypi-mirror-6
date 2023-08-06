from __future__ import unicode_literals

import os
import sys

from django.utils.translation import ugettext_lazy as _

from mutant.test import testcases
from mutant.tests.utils import BaseModelDefinitionTestCase

from . import models


PACKAGE_PATH = os.path.dirname(sys.modules[__name__].__file__)
MODULE_PATH = os.path.abspath(sys.modules[__name__].__file__)
MODELS_MODULE_PATH = os.path.abspath(models.__file__)


class FilePathFieldDefinitionTest(testcases.FieldDefinitionTestMixin,
                                  BaseModelDefinitionTestCase):
    field_definition_category = _('File')
    field_definition_cls = models.FilePathFieldDefinition
    field_definition_init_kwargs = {'path': PACKAGE_PATH}
    field_values = (MODULE_PATH, MODELS_MODULE_PATH)

    def test_formfield(self):
        self.field.match = r'\.pyc?$'
        self.field.save()
        formfield = self.field.construct().formfield()
        self.assertTrue(formfield.valid_value(MODULE_PATH))
        invalid_path = os.path.abspath(testcases.__file__)
        self.assertFalse(formfield.valid_value(invalid_path))
