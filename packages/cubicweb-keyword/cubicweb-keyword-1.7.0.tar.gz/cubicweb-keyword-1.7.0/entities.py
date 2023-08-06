"""entity classes for classification schemes entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.deprecation import  deprecated

from cubicweb.mixins import MI_REL_TRIGGERS, TreeMixIn
from cubicweb.entities import AnyEntity, fetch_config, adapters
from cubicweb.interfaces import ITree
from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance

class Classification(AnyEntity):
    __regid__ = 'Classification'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])


class ClassificationITreeAdapter(EntityAdapter):
    __regid__ = 'ITree'
    __select__ = is_instance('Classification')

    def root(self):
        """returns the root object"""
        return None

    def parent(self):
        """returns the parent entity"""
        return None

    def iterparents(self):
        """returns parent entities"""
        yield self

    def children(self, entities=True):
        """returns the item's children"""
        return self.entity.related('included_in', 'object', entities=entities)

    def children_rql(self):
        """XXX returns RQL to get children"""
        return self.entity.related_rql('included_in', 'object')

    def is_leaf(self):
        """returns true if this node as no child"""
        return bool(self.children())

    def is_root(self):
        """returns true if this node has no parent"""
        return True

    @deprecated('[3.6] was specific to external project')
    def first_level_keywords(self):
        return self.req.execute('Any K,N ORDERBY N WHERE K included_in C, '
                                'NOT K subkeyword_of KK, K name N, '
                                'C eid %(x)s', {'x': self.eid})


class Keyword(AnyEntity):
    __regid__ = 'Keyword'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])


class KeywordITreeAdapter(adapters.ITreeAdapter):
    __select__ = is_instance('Keyword', 'CodeKeyword')
    tree_relation = 'subkeyword_of'

    @property
    def classification(self):
        if self.entity.included_in:
            return self.entity.included_in[0]
        return None

    def parent(self):
        """ITree + IBreadcrumbs implementation"""
        try:
            return self.entity.related(self.tree_relation, self.child_role,
                                entities=True)[0]
        except (KeyError, IndexError):
            return self.classification

    def iterparents(self):
        """returns parent keyword entities,
           without the root classification
        """
        if self.entity.subkeyword_of:
            parent = self.entity.subkeyword_of[0]
            while parent is not None:
                yield parent
                if parent.subkeyword_of:
                    parent = parent.subkeyword_of[0]
                else:
                    parent = None

    def iterchildren(self):
        """returns children entities"""
        if self.reverse_subkeyword_of:
            child = self.reverse_subkeyword_of[0]
            while child is not None:
                yield child
                if child.reverse_subkeyword_of:
                    child = child.reverse_subkeyword_of[0]
                else:
                    child = None

    def recurse_children(self, _done=None):
        """returns strict descendents"""
        if _done is not None and self.entity.eid in _done:
            return
        if _done is not None:
            _done.add(self.entity.eid)
            yield self.entity
        else:
            _done = set()
        for child in self.children():
            for entity in child.cw_adapt_to('ITree').recurse_children(_done):
                yield entity

class CodeKeyword(Keyword):
    __regid__ = 'CodeKeyword'
    rest_attr = 'code'
    fetch_attrs, cw_fetch_order = fetch_config(['code','name'])

    def dc_title(self):
        return u'%s - %s' % (self.code, self.name)


class ClassifiableMixIn(object):
    """mixin automatically plugged to entity types supporting the applied_to
    relation
    """
    def classification_keywords(self, name):
        """return keywords of the given classification linked to this entity"""
        return self.req.execute('Any K, KN WHERE K applied_to X, X eid %(x)s, '
                                'K name KN, K included_in CS, CS name %(name)s',
                                {'x': self.eid, 'name': name}, 'x')

MI_REL_TRIGGERS[('applied_to', 'object')] = ClassifiableMixIn
