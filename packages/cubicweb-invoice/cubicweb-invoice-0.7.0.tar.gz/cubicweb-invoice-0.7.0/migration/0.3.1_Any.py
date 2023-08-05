#Invoice workflow migration

waiting_command  = add_state(_('waiting command'), 'Invoice', initial=True)
planned = rql('State S WHERE S state_of ET, ET name "Invoice", S name "planned"')[0][0]
add_transition(_('command received'), 'Invoice', (waiting_command,), planned)

