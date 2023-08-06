from cubicweb.devtools.testlib import CubicWebTC

class SecurityTC(CubicWebTC):
    def setup_database(self):
        req = self.request()
        cwgroup = self.execute('Any U WHERE U is ET, U name "CWGroup"').get_entity(0,0)
        self.classif1 = self.request().create_entity('Classification', name=u"classif1", classifies=cwgroup)
        self.kw1 = req.create_entity('Keyword', name=u'kw1', included_in=self.classif1)

    def test_nonregr_keyword_selection_as_guest(self):
        self.login('anon')
        self.execute('Any X ORDERBY Z WHERE X modification_date Z, K eid %(k)s, K applied_to X', {'k':self.kw1.eid})

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

