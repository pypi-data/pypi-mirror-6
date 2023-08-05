from yams.buildobjs import (EntityType, SubjectRelation, String, RichString,
                            RelationDefinition)
from yams.reader import context
from cubicweb.schema import RRQLExpression, RQLConstraint


_ = unicode

class Person(EntityType):
    """a physical person"""
    surname   = String(required=True, fulltextindexed=True, indexed=True, maxsize=64)
    firstname = String(fulltextindexed=True, maxsize=64)
    civility  = String(required=True, internationalizable=True,
                       vocabulary=(_('Mr'), _('Ms'), _('Mrs')),
                       default='Mr')

    description        = RichString(fulltextindexed=True)

    if 'PhoneNumber' in context.defined: # from addressbook package
        phone = SubjectRelation('PhoneNumber', composite='subject')
    if 'PostalAddress' in context.defined:
        postal_address = SubjectRelation('PostalAddress', composite='subject')
    if 'IMAddress' in context.defined:
        im_address = SubjectRelation('IMAddress', composite='subject')



class use_email(RelationDefinition):
    """person's email account"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
        }
    subject = "Person"
    object = "EmailAddress"
    cardinality = '*?'
    composite = 'subject'


class primary_email(RelationDefinition):
    """person's primary email account"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
        }
    subject = "Person"
    object = "EmailAddress"
    cardinality = '??'
    constraints= [RQLConstraint('S use_email O')]

