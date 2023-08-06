"""Specific views for keywords / classification schemes

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb import Unauthorized
from cubicweb.predicates import is_instance, rql_condition, relation_possible
from cubicweb.view import EntityView
from cubicweb.web import stdmsgs, uicfg, component, facet
from cubicweb.web.views import primary, basecontrollers, treeview
from cubicweb.web.views.ajaxcontroller import ajaxfunc


_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('*', 'applied_to', '*'), 'hidden')
_pvs.tag_subject_of(('*', 'applied_to', '*'), 'hidden')
_pvs.tag_object_of(('*', 'included_in', 'Classification'), 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('CodeKeyword', 'included_in', 'Classification'), True)
_abaa.tag_object_of(('Keyword', 'included_in', 'Classification'), True)
_abaa.tag_object_of(('CodeKeyword', 'subkeyword_of', 'CodeKeyword'), True)
_abaa.tag_object_of(('Keyword', 'subkeyword_of', 'Keyword'), True)


# classification views ########################################################

class ClassificationPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Classification')

    def render_entity_attributes(self, entity):
        pass

    def render_entity_relations(self, entity):
        rset = self._cw.execute('Any K ORDERBY N WHERE K included_in C, '
                                'NOT K subkeyword_of KK, K name N, '
                                'C eid %(x)s', {'x': entity.eid})
        self.wview('treeview', rset, 'null')


# keyword views ###############################################################

class KeywordPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Keyword')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h1 class="titleUnderline">%s</h1>'
               % xml_escape(entity.dc_long_title()))
        rset = entity.related('subkeyword_of','object')
        self.wview('treeview', rset, 'null')


class KeywordComboBoxView(treeview.TreePathView):
    """display keyword in edition's combobox"""
    __regid__ = 'combobox'
    __select__ = is_instance('Keyword', 'Classification')

    item_vid = 'text'
    separator = u' > '

# skos views ############################################################

SKOS_OPENING_ROOT=u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rdfs [
	<!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	<!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#">
	<!ENTITY dc "http://purl.org/dc/elements/1.1/">
	<!ENTITY dct "http://purl.org/dc/terms/">
]>
<rdf:RDF  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:skos="http://www.w3.org/2004/02/skos/core#">
'''
SKOS_CLOSING_ROOT = u'</rdf:RDF>'

class SkosView(EntityView):
    __regid__ = 'skos'
    content_type = 'application/xml'
    templatable = False
    __select__ = is_instance('Keyword', 'Classification')

    def call(self, **kwargs):
        self.w(SKOS_OPENING_ROOT)
        for i in xrange(self.rset.rowcount):
             self.cell_call(i, 0)
        self.w(SKOS_CLOSING_ROOT)

    def cell_call(self, row, col):
        self.wview('skositemview', self.rset, row=row, col=col)

class SkosItemView(EntityView):
    __regid__ = 'skositemview'
    content_type = 'application/xml'
    __select__ = is_instance('Keyword', 'Classification')

    def cell_call(self, row, col, show_parent=True, stop=False):
        w = self.w
        entity = self.complete_entity(row, col)
        eschema = entity.e_schema
        w(u'<skos:%s>' % eschema)
        w(u'<skos:prefLabel>%s</skos:prefLabel>' % xml_escape(entity.name))
        if not stop:
            if show_parent and not entity.is_root():
                par = entity.parent()
                w(u'<skos:broader>')
                par.view('skositemview', show_parent=False, stop=True, w=self.w)
                w(u'</skos:broader>')
            for child in entity.children(entities=True):
                w(u'<skos:narrower>')
                self.wview('skositemview', child.as_rset(), show_parent=False)
                w(u'</skos:narrower>')
        w(u'</skos:%s>' % eschema)


# keyword component ###########################################################

class KeywordBarVComponent(component.EntityVComponent):
    """the keywords path bar: display keywords of a tagged entity"""
    __regid__ = 'keywordsbar'
    __select__ = (component.EntityVComponent.__select__ &
                  relation_possible('applied_to', 'object', 'Keyword'))
    context = 'header'
    order = 152
    htmlclass = 'navigation'

    def get_keywords(self):
        """helper method for subclasses redefinition"""
        entity = self.cw_rset.get_entity(0, 0)
        return entity.related('applied_to', 'object')

    def call(self, **kwargs):
        rset = self.get_keywords()
        if rset:
            self.w(u'<div class="%s" id="%s">\n' % (self.div_class(), self.div_id()))
            self.w(u'<span>%s</span>&nbsp;' % self._cw._('keywords:'))
            self.wview('csv', rset, 'null', done=set())
            self.w(u'</div>\n')
        else:
            self.w(u'<div class="%s hidden" id="%s"></div>\n' % (
                self.div_class(), self.div_id()))


class AddKeywordVComponent(component.EntityVComponent):
    """the 'add keyword' component"""
    __regid__ = 'addkeywords'
    __select__ = component.EntityVComponent.__select__ & \
                 relation_possible('applied_to', 'object', 'Keyword', action='add') & \
                 rql_condition('X is ET, CL classifies ET')

    context = 'header'
    order = 153
    htmlclass = 'navigation'

    def entity_call(self, entity, view=None):
        self.add_js(['cubicweb.widgets.js', 'cubes.keyword.js'])
        self._cw.add_css('cubicweb.suggest.css')
        self.w(u'<table><tr><td>')
        self.w(u'<a class="button sglink" href="javascript: showKeywordSelector(%s, \'%s\', \'%s\');">%s</a></td>' % (
            entity.eid, self._cw._(stdmsgs.BUTTON_OK[0]),
            self._cw._(stdmsgs.BUTTON_CANCEL[0]), self._cw._('add keywords')))
        self.w(u'<td><div id="kwformholder"></div>')
        self.w(u'</td></tr></table>')


# applied_to relation facet ####################################################

class AppliedToFacet(facet.RelationFacet):
    __regid__ = 'applied-to-facet'
    rtype = 'applied_to'
    role = 'object'
    target_attr = 'name'

    def rset_vocabulary(self, rset):
        _ = self._cw._
        vocab = []
        scheme = None
        for e in sorted(rset.entities(),
                        key=lambda e: (e.cw_adapt_to('ITree').classification.name,
                                       e.view('combobox'))):
            classification_name = e.cw_adapt_to('ITree').classification.name
            if scheme != classification_name:
                vocab.append( (_(classification_name), None) )
            vocab.append( (e.view('combobox'), e.eid) )
        return vocab


class ClassificationFacet(facet.RelationFacet):
    """abstract per-classification facet

    subclasses must define their own id the classification name, e.g :

    class Classifaction1Facet(ClassificationFacet):
        __regid__ = 'classif1'
        classification = u'classification1'

    """
    __abstract__ = True
    classification = None
    rtype = 'applied_to'
    role = 'object'

    def vocabulary(self):
        """return vocabulary for this facet, eg a list of 2-uple (label, value)
        """
        rqlst = self.rqlst
        rqlst.save_state()
        try:
            mainvar = self.filtered_variable # X
            keyword_var = rqlst.make_variable() # K
            keyword_name_var = rqlst.make_variable() # KN
            classif_var = rqlst.make_variable() # C
            classif_name_var = rqlst.make_variable() # CN
            rqlst.add_relation(keyword_var, 'applied_to', mainvar) # K applied_to X
            rqlst.add_relation(keyword_var, 'name', keyword_name_var) # K name KN
            rqlst.add_relation(keyword_var, 'included_in', classif_var) # K included_in C
            # C name "classification-name"
            rqlst.add_constant_restriction(classif_var, 'name', self.classification, 'String')
            rqlst.add_selected(keyword_var)
            rqlst.add_selected(keyword_name_var)
            # ORDERBY KN
            rqlst.add_sort_var(keyword_name_var, True)
            try:
                rset = self._cw.execute(rqlst.as_string(), self.rset.args,
                                        self.rset.cachekey)
            except Unauthorized:
                return []
        finally:
            rqlst.recover()
        return self.rset_vocabulary(rset)

    @property
    def title(self):
        return self._cw._(self.classification)

    def support_and(self):
        return False

# add some classification schema related methods to the Jsoncontroller ########

@ajaxfunc(output_type='json')
def js_possible_keywords(self, eid):
    rql = ('DISTINCT Any N WHERE K is Keyword, K name N, NOT K applied_to X, '
           'X eid %(x)s, K included_in C, C classifies ET, X is ET')
    rset = self.cursor.execute(rql, {'x' : eid, 'u' : self._cw.user.eid}, 'x')
    return [name for (name,) in rset]

@ajaxfunc(output_type='json')
def js_add_keywords(self, eid, kwlist):
    msg = self._cw._('keywords applied')
    kwrset = self.cursor.execute('Any K,N,C WHERE K is Keyword, K name N, K included_in C, '
                                 'C classifies ET, X eid %(x)s, X is ET',
                                 {'x' : eid}, 'x')
    if not kwrset:
        return self._cw._('No suitable classification scheme found')
    classification = kwrset[0][2] # XXX what if we have several classifications ?
    valid_keywords = set(kwname for _, kwname,_ in kwrset)
    user_keywords = set(kwlist)
    invalid_keywords = sorted(user_keywords - valid_keywords)
    kweids = dict( (kwname, str(kweid)) for kweid, kwname, _ in kwrset if kwname in user_keywords )
    if invalid_keywords:
        for keyword in invalid_keywords:
            neweid = self.cursor.execute('INSERT Keyword K: K name %(name)s, K included_in C WHERE C eid %(c)s',
                                         {'name' : keyword, 'c' : classification}, 'c')[0][0]
            kweids[keyword] = str(neweid)
    if kweids:
        self.cursor.execute('SET KW applied_to X WHERE X eid %%(x)s, KW eid IN (%s)'
                            % ','.join(kweids.values()), {'x' : eid}, 'x')
    return msg
