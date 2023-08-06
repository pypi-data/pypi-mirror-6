from cubicweb.devtools.testlib import CubicWebTC

from cubicweb import ValidationError


class ClassificationHooksTC(CubicWebTC):

    def setup_database(self):
        req = self.request()
        # classification for CWGroup
        cwgroup = self.execute('Any U WHERE U is ET, U name "CWGroup"').get_entity(0,0)
        self.classif1 = self.request().create_entity('Classification', name=u"classif1", classifies=cwgroup)
        self.kwgroup = req.create_entity('Keyword', name=u'kwgroup', included_in=self.classif1)
        # classification for CWUser
        cwuser = self.execute('Any U WHERE U is ET, U name "CWUser"').get_entity(0,0)
        self.classif2 = self.request().create_entity('Classification', name=u"classif2", classifies=cwuser)
        self.kwuser = req.create_entity('Keyword', name=u'kwuser', included_in=self.classif2)

    def test_application_of_bad_keyword_fails(self):
        self.execute('SET K applied_to G WHERE G is CWGroup, K eid %(k)s',
                     {'k':self.kwuser.eid})
        self.assertRaises(ValidationError, self.commit)

    def test_creating_a_new_subkeyword_sets_included_in(self):
        req = self.request()
        kwgroup2 = req.create_entity('Keyword', name=u'kwgroup2', subkeyword_of=self.kwgroup)
        self.commit()
        rset = self.execute('Any N WHERE C name N, K included_in C, K eid %(k)s', {'k':kwgroup2.eid})
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset[0][0], 'classif1')


    def test_cannot_create_subkeyword_from_other_classification(self):
        self.execute('SET K1 subkeyword_of K2 WHERE K1 eid %(k1)s, K2 eid %(k2)s',
                     {'k1':self.kwgroup.eid, 'k2':self.kwuser.eid})
        self.assertRaises(ValidationError, self.commit)


    def test_cannot_create_cycles(self):
        req = self.request()
        # direct obvious cycle
        self.execute('SET K1 subkeyword_of K2 WHERE K1 eid %(k1)s, K2 eid %(k2)s',
                          {'k1':self.kwgroup.eid, 'k2':self.kwuser.eid})
        self.assertRaises(ValidationError, self.commit)
        # testing indirect cycles
        kwgroup2 =  req.create_entity('Keyword', name=u'kwgroup2', included_in=self.classif1, subkeyword_of=self.kwgroup)
        self.execute('SET K subkeyword_of K2 WHERE K eid %(k)s, K2 eid %(k2)s',
                     {'k':self.kwgroup.eid, 'k2':kwgroup2.eid})
        self.assertRaises(ValidationError, self.commit)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
