# -*- coding: utf-8 -*-

import re
from AccessControl import getSecurityManager, Unauthorized
from zope.component import queryUtility, getMultiAdapter
from Products.Five import BrowserView
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from redturtle.sendto_extension import _
from redturtle.sendto_extension.interfaces import ISendtoExtensionSettings

class SendtoExtensionView(BrowserView):
    """Service view for the send_to extension"""

    i18n_send_to_members = _('Send to site members')
    i18n_send_to_members_help =  _('send_to_members_help',
                                   default=u'Select a set of site members to send this page to.\n'
                                           u'Start typing some character, then select from the dropdown.')
    i18n_send_to_groups = _('Send to groups')
    i18n_send_to_groups_help = _('send_to_groups_help',
                                 u'Select a set of groups to which members send this page to.\n'
                                 u'Start typing some character, then select from the dropdown.')
    i18n_send_to_members_bcc = _('Send to site members (using BCC)')
    i18n_send_to_members_help_bcc =  _('send_to_members_help_bcc',
                                       default=u'Select a set of site members to send this page to.\n'
                                               u'Start typing some character, then select from the dropdown.\n'
                                               u'Users in this list will not be revealed to other recipients')
    i18n_send_to_groups_bcc = _('Send to groups (using BCC)')
    i18n_send_to_groups_help_bcc = _('send_to_groups_help_bcc',
                                     default=u'Select a set of groups to which members send this page to.\n'
                                             u'Start typing some character, then select from the dropdown.\n'
                                             u'Users inside groups in this list will not be revealed to other recipients')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        request.set('disable_border', 1)

    def __call__(self):
        if self.request.form.get('form.submitted') and self.send():
            return self.request.response.redirect(
                    self.context.absolute_url() + '/@@' + self.__name__)
        return self.index()

    def _members_email(self, members_id):
        if members_id:
            self.can_query_members(raiseError=True)
        acl_users = getToolByName(self.context, 'acl_users')
        emails = []
        for member_id in members_id:
            member_data = acl_users.searchUsers(name=member_id, exact_match=True)
            if len(member_data)>0:
                member = acl_users.getUserById(member_data[0].get('login'))
                if member.getProperty('email'):
                    emails.append(member.getProperty('email'))
        return emails

    def _groups_email(self, groups_id):
        if groups_id:
            self.can_query_groups(raiseError=True)
        acl_users = getToolByName(self.context, 'acl_users')
        emails = []
        for group_id in groups_id:
            group_data = acl_users.searchGroups(name=group_id, exact_match=True)
            if len(group_data)>0:
                group = acl_users.getGroupById(group_data[0].get('groupid'))
                if group.getProperty('email'):
                    emails.append(group.getProperty('email'))
                # Now emails from users
                emails.extend(self._members_email(group.getGroupMemberIds()))
        return emails

    def send(self):
        """Send e-mail to all recipients, loading e-mail from member is needed and doing security check"""
        # first of all: captcha protection if needed
        if self.capcha_enabled():
            if not self.context.restrictedTraverse('@@captcha').verify():
                ptool = getToolByName(self.context, 'plone_utils') 
                ptool.addPortalMessage(_('Captcha protection code is wrong. Please retry'), type="error")
                return False
        
        form = self.request.form
        sender = form.get('send_from_address', None)
        if not sender and not self.can_set_sender_mail():
            sender = getToolByName(self.context, 'portal_membership').getAuthenticatedMember().getProperty('email')

        message = form.get('message', '')
        if self.can_send_to_multiple_recipients():
            send_to_address = form.get('send_to_address', '').strip()
            send_to_address = re.findall(r"[\w@.-_']+", send_to_address)
            send_to_address_bcc = form.get('send_to_address_bcc', '').strip()
            send_to_address_bcc = re.findall(r"[\w@.-_']+", send_to_address_bcc)
        else:
            # whatever we get, it must be a single email address
            send_to_address = [send_to_address]
            send_to_address_bcc = [send_to_address_bcc]

        send_to_members = form.get('send_to_members', [])
        send_to_members_bcc = form.get('send_to_members_bcc', [])
        send_to_groups = form.get('send_to_groups', [])
        send_to_groups_bcc = form.get('send_to_groups_bcc', [])
        cc_me = form.get('cc_me', False)
        
        # If we have items in both a list and in the bcc version, remove from the list
        send_to_address = [x for x in send_to_address if x not in send_to_address_bcc]
        send_to_members = [x for x in send_to_members if x not in send_to_members_bcc]
        send_to_groups = [x for x in send_to_groups if x not in send_to_groups_bcc]

        # get email from principals
        members_email = self._members_email(send_to_members)
        members_email_bcc = self._members_email(send_to_members_bcc)
        groups_email = self._groups_email(send_to_groups)
        groups_email_bcc = self._groups_email(send_to_groups_bcc)
        if cc_me:
            member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
            members_email.append(member.getProperty('email'))

        return self._send_mail(sender=sender,
                               message=message,
                               to=send_to_address + members_email + groups_email,
                               bcc=send_to_address_bcc + send_to_members_bcc + send_to_groups_bcc,
                               )

    def _repl_interpolation(self, text, sender, message):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        portal_url = portal_state.portal_url()
        text = text.replace('${site_name}', portal.title_or_id().decode('utf-8'))
        text = text.replace('${site_description}', portal.getProperty('description').decode('utf-8'))
        text = text.replace('${site_url}', portal_url.decode('utf-8'))
        text = text.replace('${title}', self.context.title_or_id().decode('utf-8'))
        text = text.replace('${url}', self.context.absolute_url().decode('utf-8'))
        text = text.replace('${sender}', sender.decode('utf-8'))
        # message intentation
        message = "\n".join(['\t'+x for x in message.strip().splitlines()])
        text = text.replace('${comment}', message)
        return text

    def _send_mail(self, sender, message, to=[], bcc=[]):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ISendtoExtensionSettings, check=False)
        subject = settings.email_subject
        body = settings.email_body
        subject = self._repl_interpolation(subject, sender, '')
        body = self._repl_interpolation(body, sender, message)
        mail_host = getToolByName(self.context, 'MailHost')
        to = [x for x in to if mail_host.validateSingleEmailAddress(x) and x not in bcc]
        bcc = [x for x in bcc if mail_host.validateSingleEmailAddress(x)]
        ptool = getToolByName(self.context, 'plone_utils')
        if not sender:
             ptool.addPortalMessage(_('No sender address provided'), type="error")
             return False
        if not to and not bcc:
             ptool.addPortalMessage(_('No recipients'), type="error")
             return False
        
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ISendtoExtensionSettings, check=False)
        if not settings.use_mail_for_sender:
            sender = getToolByName(self.context, 'portal_url').getPortalObject().getProperty('email_from_address')
        
        mail_host.secureSend(body, to, sender, subject=subject,
                             mbcc=bcc, subtype='plain', charset='utf-8')
        ptool.addPortalMessage(_('Message sent'))
        return True

    def capcha_enabled(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        if portal_state.anonymous():
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(ISendtoExtensionSettings, check=False)
            if settings.captcha=='collective.recaptcha':
                return True
        return False

    def load_users_from_req(self, name):
        """Get user ids from request and load users data"""
        acl_users = getToolByName(self.context, 'acl_users')
        user_ids = self.request.get(name, [])
        results = []
        for user_id in user_ids:
            user = acl_users.getUserById(user_id)
            if user:
                results.append({'title': user.getProperty('fullname') or user_id, 'value': user_id})
        return results

    def load_groups_from_req(self, name):
        """Get group ids from request and load groups data"""
        acl_users = getToolByName(self.context, 'acl_users')
        groups_ids = self.request.get(name, [])
        results = []
        for group_id in groups_ids:
            group = acl_users.getGroupById(group_id)
            if group:
                results.append({'title': group.getProperty('title') or group_id, 'value': group_id})
        return results

    def can_query_members(self, raiseError=False):
        sm = getSecurityManager()
        can_do = sm.checkPermission('SendTo Extension: query site members', self.context)
        if not raiseError:
            return can_do
        if not can_do:
            raise Unauthorized("You can't query site members")
        return True

    def can_query_groups(self, raiseError=False):
        sm = getSecurityManager()
        can_do = sm.checkPermission('SendTo Extension: query groups', self.context)
        if not raiseError:
            return can_do
        if not can_do:
            raise Unauthorized("You can't query groups")
        return True

    def can_send_to_multiple_recipients(self, raiseError=False):
        sm = getSecurityManager()
        can_do = sm.checkPermission('SendTo Extension: send to multiple recipients', self.context)
        if not raiseError:
            return can_do
        if not can_do:
            raise Unauthorized("You can't send to  multiple recipients")
        return True

    def can_set_sender_mail(self):
        portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
        if portal_state.anonymous():
            return True
        member = portal_state.member()
        if not member.getProperty('email'):
            return True
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(ISendtoExtensionSettings, check=False)
        return not settings.force_member_email
