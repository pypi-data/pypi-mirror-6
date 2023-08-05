from pprint import pprint
import os

from ..models import *
from .common import ModelTestCase
from .models import *



class DjangoORMTest(ModelTestCase):

    def test_reverse_field_registration(self):
        self.assertTrue(hasattr(A, 'b_set'))
        self.assertTrue(A._meta.get_field_by_name('b'))

        self.assertTrue(hasattr(A, 'c_set'))
        self.assertTrue(A._meta.get_field_by_name('c'))


