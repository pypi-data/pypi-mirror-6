from yams.buildobjs import RelationDefinition

class applied_to(RelationDefinition):
    subject = 'Keyword'
    object = ('CWUser', 'CWGroup')
