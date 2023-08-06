from __future__ import with_statement
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb import ValidationError


class KeywordHooksTC(CubicWebTC):

    def setup_database(self):
        cwgroup = self.execute('Any U WHERE U is ET, U name "CWGroup"').get_entity(0,0)
        self.classif1 = self.request().create_entity('Classification', name=u"classif1", classifies=cwgroup)

    def test_keyword_add1(self):
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', subkeyword_of=kw2, included_in=self.classif1)
        kw4 = req.create_entity('Keyword', name=u'kw4', subkeyword_of=kw3, included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw5', subkeyword_of=kw4, included_in=self.classif1)
        self.commit()
        parent = kw1
        child = kw5
        self.assertItemsEqual([kw.name for kw in child.cw_adapt_to('ITree').iterparents()], ['kw4', 'kw3', 'kw2', 'kw1'])
        self.assertItemsEqual([kw.name for kw in child.descendant_of], ['kw4', 'kw3', 'kw2', 'kw1'])
        self.assertItemsEqual([kw.name for kw in parent.reverse_descendant_of], ['kw5', 'kw4', 'kw3', 'kw2'])
        self.assertItemsEqual([kw.name for kw in parent.cw_adapt_to('ITree').recurse_children()], ['kw5', 'kw4', 'kw3', 'kw2'])

    def test_keyword_add2(self):
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', included_in=self.classif1)
        kw4 = req.create_entity('Keyword', name=u'kw4', subkeyword_of=kw3, included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw5',  subkeyword_of=kw4, included_in=self.classif1)
        self.commit()
        self.execute('SET K3 subkeyword_of K2 WHERE K3 eid %(kw3)s, K2 eid %(kw2)s',
                     {'kw3':kw3.eid, 'kw2':kw2.eid})
        self.commit()
        parent = kw1
        child = kw5
        self.assertItemsEqual([kw.name for kw in child.cw_adapt_to('ITree').iterparents()], ['kw4', 'kw3', 'kw2', 'kw1'])
        self.assertItemsEqual([kw.name for kw in child.descendant_of], ['kw4', 'kw3', 'kw2', 'kw1'])
        self.assertItemsEqual([kw.name for kw in parent.reverse_descendant_of], ['kw5', 'kw4', 'kw3', 'kw2'])
        self.assertItemsEqual([kw.name for kw in parent.cw_adapt_to('ITree').recurse_children()], ['kw5', 'kw4', 'kw3', 'kw2'])

    def test_keyword_add3(self):
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', included_in=self.classif1)
        kw4 = req.create_entity('Keyword', name=u'kw4', included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw5', subkeyword_of=kw4, included_in=self.classif1)
        self.commit()
        self.execute('SET K2 subkeyword_of K3 WHERE K2 eid %(k2)s, K3 eid %(k3)s',
                     {'k2': kw4.eid, 'k3': kw3.eid})
        self.execute('SET K3 subkeyword_of K4 WHERE K3 eid %(k3)s, K4 eid %(k4)s',
                     {'k3': kw3.eid, 'k4': kw2.eid})
        self.commit()
        child  = kw5
        parent = kw1
        self.assertItemsEqual([kw.name for kw in child.descendant_of], ['kw4', 'kw3', 'kw2', 'kw1'])
        # XXX check the order of iterparents
        self.assertItemsEqual([kw.name for kw in child.cw_adapt_to('ITree').iterparents()], ['kw4', 'kw3', 'kw2', 'kw1'])
        self.assertItemsEqual([kw.name for kw in parent.cw_adapt_to('ITree').recurse_children()], ['kw2', 'kw3', 'kw4', 'kw5'])
        self.assertItemsEqual([kw.name for kw in parent.reverse_descendant_of], ['kw2', 'kw3', 'kw4', 'kw5'])

    def test_keyword_add4(self):
        req = self.request()
        kw0 = req.create_entity('Keyword', name=u'kw0', included_in=self.classif1)
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', included_in=self.classif1)
        kw4 = req.create_entity('Keyword', name=u'kw4', included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw5',  subkeyword_of=kw4, included_in=self.classif1)
        self.execute('SET K3 subkeyword_of K2 WHERE K3 eid %(kw3)s, K2 eid %(kw2)s',
                     {'kw2': kw2.eid, 'kw3': kw3.eid})
        self.commit();
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw1', 'kw2'])
        self.execute('SET K3 descendant_of K0 WHERE K3 eid %(kw3)s, K0 eid %(kw0)s',
                      {'kw3': kw3.eid, 'kw0': kw0.eid})
        self.commit()
        kw3.cw_clear_all_caches()
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw0', 'kw1', 'kw2'])
        self.execute('SET K3 descendant_of K4 WHERE K3 eid %(kw3)s, K4 eid %(kw4)s',
                      {'kw3': kw3.eid, 'kw4': kw4.eid})
        self.commit()
        kw3.cw_clear_all_caches()
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw0', 'kw1', 'kw2', 'kw4'])
        self.execute('SET K3 descendant_of K5 WHERE K3 eid %(kw3)s, K5 eid %(kw5)s',
                       {'kw3': kw3.eid, 'kw5': kw5.eid})
        self.commit()
        kw3.cw_clear_all_caches()
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw0', 'kw1', 'kw2', 'kw4', 'kw5'])

    def test_keyword_update1(self):
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', included_in=self.classif1)
        kw4 = req.create_entity('Keyword', name=u'kw4', included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw5',  subkeyword_of=kw4, included_in=self.classif1)
        self.execute('SET K3 subkeyword_of K2 WHERE K3 eid %(kw3)s, K2 eid %(kw2)s',
                      {'kw3': kw3.eid, 'kw2': kw2.eid})
        self.commit();
        kw3 =  req.entity_from_eid(kw3.eid)
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw1', 'kw2'])
        self.execute('SET K3 subkeyword_of K4 WHERE K3 eid %(kw3)s, K4 eid %(kw4)s',
                      {'kw3': kw3.eid, 'kw4': kw4.eid})
        self.commit()
        kw3.cw_clear_all_caches()
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw4'])
        self.execute('SET K3 subkeyword_of K5 WHERE K3 eid %(kw3)s, K5 eid %(kw5)s',
                     {'kw3': kw3.eid, 'kw5': kw5.eid})
        self.commit()
        kw3.cw_clear_all_caches()
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw4', 'kw5'])

    def test_keyword_descendant_of(self):
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', subkeyword_of=kw1, included_in=self.classif1)
        self.commit()
        self.assertItemsEqual([kw.name for kw in kw2.descendant_of], ['kw1', ])
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw1', ])
        self.assertItemsEqual([kw.name for kw in kw1.reverse_descendant_of], ['kw3', 'kw2'])
        self.assertItemsEqual([kw.name for kw in kw1.cw_adapt_to('ITree').recurse_children()], ['kw2', 'kw3'])
        kw0 = req.create_entity('Keyword', name=u'kw0', included_in=self.classif1)
        self.execute('SET K1 subkeyword_of K0 WHERE K1 eid %(kw1)s, K0 eid %(kw0)s',
                      {'kw1': kw1.eid, 'kw0': kw0.eid})
        self.commit();
        kw1.cw_clear_all_caches()
        kw2.cw_clear_all_caches()
        kw3.cw_clear_all_caches()
        self.assertItemsEqual([kw.name for kw in kw0.cw_adapt_to('ITree').recurse_children()], ['kw1', 'kw2', 'kw3'])
        self.assertItemsEqual([kw.name for kw in kw0.reverse_descendant_of], ['kw3', 'kw2', 'kw1'])
        self.assertItemsEqual([kw.name for kw in kw1.descendant_of], ['kw0',])
        self.assertItemsEqual([kw.name for kw in kw2.descendant_of], ['kw1', 'kw0'])
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], ['kw1', 'kw0'])


    def test_keyword_delete(self):
        """*after_delete_relation* of ``subkeyword_of``
        """
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', subkeyword_of=kw2, included_in=self.classif1)
        kw4 = req.create_entity('Keyword', name=u'kw4', subkeyword_of=kw3, included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw5',  subkeyword_of=kw4, included_in=self.classif1)
        self.commit()
        self.execute('DELETE K subkeyword_of K3 WHERE K is Keyword, K eid %(kw3)s',
                     {'kw3':kw3.eid})
        self.commit()
        self.assertItemsEqual([kw.name for kw in kw3.cw_adapt_to('ITree').iterparents()], [])
        self.assertItemsEqual([kw.name for kw in kw3.descendant_of], [])
        self.assertItemsEqual([kw.name for kw in kw3.reverse_descendant_of], ['kw5', 'kw4'])
        self.assertItemsEqual([kw.name for kw in kw3.cw_adapt_to('ITree').recurse_children()], ['kw5', 'kw4'])

    def test_no_add_descendant_cycle(self):
        """no ``descendant_of`` cycle"""
        req = self.request()
        kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)
        kw2 = req.create_entity('Keyword', name=u'kw2', subkeyword_of=kw1, included_in=self.classif1)
        kw3 = req.create_entity('Keyword', name=u'kw3', subkeyword_of=kw2, included_in=self.classif1)
        self.commit()
        rql = 'SET K1 descendant_of K3 WHERE K1 eid %(kw1)s, K3 eid %(kw3)s' % {'kw1':kw1.eid,  'kw3':kw3.eid}
        self.assertRaises(ValidationError, self.execute, rql)
        self.rollback()
        kw4 = req.create_entity('Keyword', name=u'kw4', included_in=self.classif1)
        kw5 = req.create_entity('Keyword', name=u'kw4', subkeyword_of=kw4, included_in=self.classif1)
        self.commit()
        with self.assertRaises(ValidationError) as cm:
            self.execute('SET K4 descendant_of K5 WHERE K4 eid %(kw4)s, K5 eid %(kw5)s' % {'kw4':kw4.eid,  'kw5':kw5.eid})

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
