# -*- coding: utf-8 -*-

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel

from z3c.form import button
from z3c.form import group
from z3c.form import field

from collective.typecriterion.interfaces import ITypesCriterionSettings
from collective.typecriterion import _


class TypeCriterionSettingsControlPanelEditForm(controlpanel.RegistryEditForm):
    """Type criterion settings form.
    """
    schema = ITypesCriterionSettings
    id = "TypeCriterionSettingsEditForm"
    label = _(u"Type criterion settings")
    description = _(u"help_type_criterion_settings_editform",
                    default=u"Manage site configuration for types criterion.\n"
                            u"New types added here will be available when managing collections criteria.")

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@type-criterion-settings")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class TypeCriterionControlPanel(controlpanel.ControlPanelFormWrapper):
    """Type criterion settings control panel.
    """
    form = TypeCriterionSettingsControlPanelEditForm
