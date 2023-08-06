# -*- coding: utf-8 -*-

from cubicweb.entities import AnyEntity


class Device(AnyEntity):
    __regid__ = 'Device'

    def dc_title(self):
        title = []
        if self.model and self.model[0].made_by:
            title.append(self.model[0].made_by[0].dc_title())
        if self.model:
            title.append(self.model[0].name)
        title.append('(%s)' % self.name)
        return ' '.join(title)

class DeviceModel(AnyEntity):
    __regid__ = 'DeviceModel'

    def dc_title(self):
        title = []
        if self.made_by and self.made_by[0]:
            title.append(self.made_by[0].dc_title())
        title.append(super(DeviceModel, self).dc_title())
        title.append('(%s)' % self.klass)
        return ' '.join(title)


