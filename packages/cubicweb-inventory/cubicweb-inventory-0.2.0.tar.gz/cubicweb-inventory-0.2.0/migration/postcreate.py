create_entity('CWGroup', name=u'staff')

device_wf = add_workflow(_('default Device workflow'), 'Device')

operational = device_wf.add_state(_('operational'), initial=True)
broken = device_wf.add_state(_('broken'))
unused = device_wf.add_state(_('unused'))

fail = device_wf.add_transition(_('fail'), operational, broken,
                                ('managers', 'owners', 'staff'))
repair = device_wf.add_transition(_('repair'), broken, operational,
                                  ('managers', 'owners', 'staff'))
unplug = device_wf.add_transition(_('unplug'), operational, unused,
                                  ('managers', 'owners', 'staff'))
replug = device_wf.add_transition(_('replug'), unused, operational,
                                  ('managers', 'owners', 'staff'))


devicemodel_wf = add_workflow(_('default DeviceModel workflow'), 'DeviceModel')

on_market = devicemodel_wf.add_state(_('on the market'), initial=True)
deprecated = devicemodel_wf.add_state(_('deprecated'))

deprecate = devicemodel_wf.add_transition(_('deprecate'), on_market, deprecated,
                                           ('managers', 'owners', 'staff'))



