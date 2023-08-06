"""This cube handles classification schemes.

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from yams.buildobjs import (EntityType, RelationType,
                            SubjectRelation, ObjectRelation, String)

from cubicweb.schema import RQLConstraint, ERQLExpression


_ = unicode

class Classification(EntityType):
    """classification schemes are used by users to classify entities.
    """
    __permissions__ = {
        'read' : ('managers', 'users', 'guests'),
        'add' : ('managers',),
        'delete' : ('managers',),
        'update' : ('managers',),
        }
    name = String(required=True, fulltextindexed=True, unique=True,
                  maxsize=128)
    classifies = SubjectRelation('CWEType',
                     # see relation type docstring
                     constraints = [RQLConstraint('RDEF to_entity O,'
                                                  'RDEF relation_type R,'
                                                  'R name "applied_to"',
                     msg="Classification is trying to classifies an EntityType "
                         "without applied_to relation")])


class classifies(RelationType):
    """entity types classified by the classification. Only entity type
    supporting the applied_to relation can be selectioned
    """


class Keyword(EntityType):
    """A keyword is like a tag but is application specific
    and used to define a classification scheme
    """
    __permissions__ = {
        'read' : ('managers', 'users', 'guests'),
        'add' : ('managers', 'users'),
        'delete' : ('managers',),
        'update' : ('managers',),
        }
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)

    subkeyword_of = SubjectRelation('Keyword', cardinality='?*',
                                    description=_('which keyword (if any) this keyword specializes'),
                                    # if no included_in set, it'll be automatically added by a hook
                                    constraints=[RQLConstraint('NOT S included_in CS1 OR EXISTS(S included_in CS2, O included_in CS2)')])
    descendant_of = SubjectRelation('Keyword')
    included_in = SubjectRelation('Classification', cardinality='1*')


class CodeKeyword(Keyword):
    """A CodeKeyword is a keyword with a code and a name
    """
    __specializes_schema__ = True
    code = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)

class subkeyword_of(RelationType):
    """a keyword can specialize another keyword"""


class included_in(RelationType):
    """a keyword is included in a classification scheme"""
    inlined = True


# define in parent application which entity types may be linked to a keyword
# by the applied_to relation

class applied_to(RelationType):
    """tagged objects"""
    fulltext_container = 'object'
    constraints = [RQLConstraint('S included_in CS, O is ET, CS classifies ET')]
