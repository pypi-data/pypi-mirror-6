# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema
from zope.i18n import translate
from zope.component.hooks import getSite
from redturtle.sendto_extension import _


class IRTSendToExtensionLayer(Interface):
    """Marker interface for redturtle.sendto_extension product layer"""


def translate_default_email_body():
    msg = _('email_body',
             default=u"You received this message because someone visiting the URL ${url} wanted to "
                     u"notify you about the page.\n"
                     u"\n"
                     u"The sender address is ${sender}, and it added this comment:\n"
                     u"\n"
                     u"${comment}\n"
                     u"\n"
                     u"--\n"
                     u"\n"
                     u"${site_name}\n"
                     u"${site_description}\n"
                     u"${site_url}\n")
    return translate(msg, context=getSite().REQUEST)


def translate_default_email_subject():
    msg = _('email_subject',
            default=u'New message from "${site_name}"')
    return translate(msg, context=getSite().REQUEST)


class ISendtoExtensionSettings(Interface):
    """Settings used in the control panel for redturtle.sendto_extension
    """

    email_subject = schema.TextLine(
            title=_(u"E-mail subject"),
            description=_('email_subject_help',
                          default=u"Subject of the e-mail that will be sent when using the form.\n"
                                  u"You can use ${url} for the sent page URL, "
                                  u"${site_url} for the URL of the site, "
                                  u"${site_name} for the name of the site, "
                                  u"${title} for the title of the document, "
                                  u"${sender} for the address of the sender, "
                                  u"${comment} for the comment from the sender."
                                  ),
            defaultFactory=translate_default_email_subject,
            required=True,
    )
    
    email_body = schema.Text(
            title=_(u"E-mail body"),
            description=_('email_body_help',
                          default=u"Body text of the e-mail that will be sent when using the form.\n"
                                  u"You can use ${url} for the sent page URL, "
                                  u"${site_url} for the URL of the site, "
                                  u"${site_name} for the name of the site, "
                                  u"${title} for the title of the document, "
                                  u"${sender} for the address of the sender, "
                                  u"${comment} for the comment from the sender."
                          ),
            defaultFactory=translate_default_email_body,
            required=True,
    )

    force_member_email = schema.Bool(
            title=_(u"Force sender email from current user"),
            description=_('force_member_email_help',
                          default=u"If checked and the send form is used by an authenticated member "
                                  u"automatically take the user email address (and do not make this editable)"
                                  ),
            default=True,
    )

    use_mail_for_sender = schema.Bool(
            title=_(u"Use provided address as sender for the message"),
            description=_('use_mail_for_sender_help',
                          default=u"If checked the mail message will use the sender address. "
                                  u"If not, the default mail configuration of the site is used."
                                  ),
            default=False,
    )

    captcha = schema.Choice(
            title=_(u"Captcha protection for anonymous users"),
            description=_('captcha_help',
                          default=u"Select if you want a captcha protection when the send form is used by anonymous "
                                  u"visitors. This is HIGHLY RECOMMENDED, expecially when send to multiple recipients "
                                  u"is enabled.\n"
                                  u"The only supported captcha right now requires you to install (and configure) "
                                  u"collective.recaptcha."
                          ),
            required=True,
            vocabulary="redturtle.sendto_extension.vocabularies.captcha"
    )
