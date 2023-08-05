from yams.buildobjs import EntityType, SubjectRelation, String, Date, Float
from cubicweb.schema import WorkflowableEntityType

_ = unicode

class Invoice(WorkflowableEntityType):
    num = String(required=True, fulltextindexed=True, indexed=True,
                 maxsize=16, description=_('invoice number'))
    emit_date = Date(description=_('emission date'))
    pay_date = Date(description=_('payment date'))
    type = String(required=True, internationalizable=True,
                  vocabulary=(_('invoice'), _('expenses'), _('credit')),
                  description=_("invoice type"), default='invoice')
    amount = Float(description=_('total amount without taxes'), required=True)
    taxes = Float(description=_('taxes on total amount'), required=True)

    credit_account = SubjectRelation('Account', cardinality='?*',
                                     description=_('account to credit'))
    debit_account = SubjectRelation('Account', cardinality='?*',
                                    description=_('account to debit'))


class Account(EntityType):
    __permissions__ = {'read': ('users', 'managers'),
                       'add': ('managers', ),
                       'update': ('managers',),
                       'delete': ('managers',),
                   }
    label = String(required=True, maxsize=128)
    account = String(required=True, maxsize=16)
