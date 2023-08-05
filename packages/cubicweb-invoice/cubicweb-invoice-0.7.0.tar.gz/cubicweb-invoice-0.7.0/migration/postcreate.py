# postcreate script. You could setup a workflow here for example

wf = add_workflow('invoice workflow', 'Invoice')
waiting_command  = wf.add_state(_('waiting command'), initial=True)
planned = wf.add_state(_(u'planned'))
toissue = wf.add_state(_(u'to issue'))
tosend  = wf.add_state(_(u'to send'))
sent    = wf.add_state(_(u'sent'))
payed   = wf.add_state(_(u'payed'))

wf.add_transition(_('command received'), waiting_command, planned)
wf.add_transition(_(u'work done'), planned, toissue)
wf.add_transition(_(u'issue'), toissue, tosend)
wf.add_transition(_(u'send'), tosend, sent)
wf.add_transition(_(u'pay'), sent, payed)
