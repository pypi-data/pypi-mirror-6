# -*- coding: utf-8 -*-

from Products.CMFPlone import PloneMessageFactory as pmf
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.registry.browser import controlpanel
from z3c.form import button
from z3c.form import group
from z3c.form import field
from redturtle.sendto_extension.interfaces import ISendtoExtensionSettings
from redturtle.sendto_extension import _


def fix_widget_style(widget):
    widget.style = u'width: 100%';
    widget.klass += u" autoresize";
    widget.rows = 15


class SendToSettingsControlPanelEditForm(controlpanel.RegistryEditForm):

    schema = ISendtoExtensionSettings
    id = "AnalyticsSettingsEditForm"
    label = _(u'"Send to" form settings')
    description = _(u"help_sendto_settings_editform",
                    default=u'Manage settings for the "Send to" form')

    @button.buttonAndHandler(pmf('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@sendto-settings")

    @button.buttonAndHandler(pmf('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    def updateWidgets(self):
        super(SendToSettingsControlPanelEditForm, self).updateWidgets()
        fix_widget_style(self.widgets['email_body'])
        fix_widget_style(self.widgets['email_subject'])


class SendToSettingsControlPanel(controlpanel.ControlPanelFormWrapper):

    form = SendToSettingsControlPanelEditForm
    #index = ViewPageTemplateFile('controlpanel.pt')

