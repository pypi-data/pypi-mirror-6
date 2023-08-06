"""template automatic tests"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest
from cubicweb.devtools.fill import ValueGenerator

import random

def random_numbers(size):
    return u''.join(random.choice('0123456789') for i in xrange(size))

class MyValueGenerator(ValueGenerator):
    def generate_Book_isbn10(self, entity, index):
        return random_numbers(10)
    def generate_Book_isbn13(self, entity, index):
        return random_numbers(13)

class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Book', 'Collection', 'Editor'))

    def list_startup_views(self):
        return ()

if __name__ == '__main__':
    unittest_main()
