"""this contains the template-specific entities' classes"""

from cubicweb.entities import AnyEntity, fetch_config

class Invoice(AnyEntity):
    __regid__ = 'Invoice'
    fetch_attrs, fetch_order = fetch_config(['num'])

    def dc_title(self):
        return u"%s #%s" % (self.type, self.num.upper())

    def dc_long_title(self):
        _ = self._cw._
        return u"%s (%s+%s) %s %s, %s %s - %s" % (
            self.dc_title(), self.amount, self.taxes,
            _('emited on'), self.printable_value('emit_date'),
            _('paid on'), self.printable_value('pay_date'),
            self.cw_adapt_to('IWorkflowable').state)


class Account(AnyEntity):
    __regid__ = 'Account'
    fetch_attrs, fetch_order = fetch_config(['label', 'account'])

    def dc_title(self):
        return u'%s - %s' % (self.account, self.label)
