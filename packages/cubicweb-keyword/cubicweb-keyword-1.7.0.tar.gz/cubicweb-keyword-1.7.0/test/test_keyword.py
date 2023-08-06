from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):

    ignored_relations = set(('descendant_of',))

    def to_test_etypes(self):
        # add cwgroup to test keyword components on entity on which they can be applied
        return set(('Classification', 'Keyword', 'CWGroup'))

    def list_startup_views(self):
        return ()

if __name__ == '__main__':
    unittest_main()
