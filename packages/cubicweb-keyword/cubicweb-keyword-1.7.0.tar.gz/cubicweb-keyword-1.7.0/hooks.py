"""specific hooks for Classification and Keyword entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from itertools import chain

from cubicweb import ValidationError
from cubicweb.server.hook import Hook, Operation, match_rtype
from yams.schema import role_name

class BeforeAddDescendantOf(Hook):
    """check indirect cycle for ``descendant_of`` relation
    """
    __regid__ = 'beforeadddescendant'
    events = ('before_add_relation', )
    __select__ = Hook.__select__ & match_rtype('descendant_of')

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        parent = self._cw.entity_from_eid(self.eidto)
        parents = set([x.eid for x in chain([parent,], parent.cw_adapt_to('ITree').iterparents())])
        children = set([x.eid for x in chain([entity], entity.cw_adapt_to('ITree').recurse_children())])
        if children & parents:
            msg = _('detected descendant_of cycle')
            raise ValidationError(self.eidfrom, {role_name(self.rtype, 'subject'): msg})


class AfterAddSubKeywordOf(Hook):
    """sets ``descendant_of`` relation
    """
    __regid__ = 'afteradddescendant'
    events = ('after_add_relation', )
    __select__ = Hook.__select__ & match_rtype('subkeyword_of')

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        parent = self._cw.entity_from_eid(self.eidto)
        SetDescendantOfKeywordOp(self._cw, parent=parent, entity=entity)

class SetIncludedInRelationHook(Hook):
    """sets the included_in relation on a subkeyword if not already set
    """
    __regid__ = 'setincludedinrelationhook'
    events = ('before_add_relation',)
    __select__ = Hook.__select__ & match_rtype('subkeyword_of')

    def __call__(self):
        # immediate test direct cycles
        if self.eidfrom == self.eidto:
            msg = self._cw._('keyword cannot be subkeyword of himself')
            raise ValidationError(self.eidfrom, {role_name(self.rtype, 'subject') : msg})
        SetIncludedInRelationOp(self._cw, vreg=self._cw.vreg,
                                eidfrom=self.eidfrom, eidto=self.eidto)



class RemoveDescendantOfRelation(Hook):
    """removes ``descendant_of`` relation

    we delete the relation for entity's parents recursively
    """
    __regid__ = 'removedescendantofrelation'
    events = ('after_delete_relation',)
    __select__ = Hook.__select__ & match_rtype('subkeyword_of')

    def __call__(self):
        parent = self._cw.entity_from_eid(self.eidto)
        for parent in chain([parent], parent.cw_adapt_to('ITree').iterparents()):
            self._cw.execute('DELETE K descendant_of P WHERE K eid %(k)s, '
                            'P eid %(p)s', {'p':parent.eid, 'k': self.eidfrom})


## operations #################################################################
class SetIncludedInRelationOp(Operation):
    """delay this operation to commit to avoid conflict with a late rql query
    already setting the relation
    """
    def precommit_event(self):
        session = self.session
        # test for indirect cycles
        self.check_cycle()
        subkw = session.entity_from_eid(self.eidfrom)
        if subkw.included_in:
            kw = session.entity_from_eid(self.eidto)
            if subkw.included_in[0].eid != kw.included_in[0].eid:
                msgid = "keywords %(subkw)s and %(kw)s belong to different classifications"
                raise ValidationError(subkw.eid, {role_name('subkeyword_of', 'subject'): session._(msgid) %
                                                  {'subkw' : subkw.eid, 'kw' : kw.eid}})
        else:
            session.execute('SET SK included_in C WHERE SK eid %(x)s, '
                            'SK subkeyword_of K, K included_in C',
                            {'x': subkw.eid})

    def check_cycle(self):
        parents = set([self.eidto])
        parent = self.session.entity_from_eid(self.eidto)
        while parent.subkeyword_of:
            parent = parent.subkeyword_of[0]
            if parent.eid in parents:
                msg = self.session._('detected subkeyword cycle')
                raise ValidationError(self.eidfrom, {role_name('subkeyword_of', 'subject'): msg})
            parents.add(parent.eid)


class SetDescendantOfKeywordOp(Operation):
    def precommit_event(self):
        """transitive closure of ``descendant_of`` relations to current entity"""
        closure = set()
        entity = self.entity
        parent = self.parent
        for parent in chain([parent, entity], parent.cw_adapt_to('ITree').iterparents()):
            for child in chain([entity], entity.cw_adapt_to('ITree').recurse_children()):
                if child.eid != parent.eid:
                    closure.add((child, parent))
        for child, parent in closure:
            descendants = [p.eid for p in child.descendant_of]
            if not parent.eid in descendants:
                child.set_relations(descendant_of=parent)
