# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.formlib import form
try:
    from Products.Five.formlib import formbase
except ImportError:
    from five.formlib import formbase
from Products.statusmessages.interfaces import IStatusMessage

from monet.calendar.event import eventMessageFactory as _
from monet.calendar.event.migrator import migrateMonetEvent

class IMigrateBlobsSchema(Interface):
    pass


class MigrateBlobs(formbase.PageForm):
    form_fields = form.FormFields(IMigrateBlobsSchema)
    label = _(u'Blobs Migration')
    description = _(u'Migrate all events images, making them use plone.app.blob')

    @form.action(_(u'Migrate events images'))
    def actionMigrate(self, action, data):
        output = migrateMonetEvent(self.context)
        IStatusMessage(self.request).addStatusMessage(output, type='info')
        return self.request.response.redirect(self.context.absolute_url())        

    @form.action(_(u'Cancel'))
    def actionCancel(self, action, data):
        return self.request.response.redirect(self.context.absolute_url())
