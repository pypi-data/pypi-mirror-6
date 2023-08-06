# -*- coding: utf-8 -*-
# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import MimeWriter
import base64
import StringIO
from smtplib import SMTPException

from zope import interface, schema, component
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.traversing.browser import absoluteURL

from Products.Silva import mangle
from Products.Silva.mail import sendmail
from Products.SilvaLayout import interfaces

from collective.captcha.form.field import Captcha
from silva.core.views import forms as silvaforms
from silva.core.views.interfaces import IHTTPResponseHeaders
from silva.pageactions.base.base import PageAction

from five import grok

_ = MessageFactory("pageactions")


class IMailForm(interface.Interface):

    to = schema.TextLine(title=_(u"To"))
    subject = schema.TextLine(title=_(u"Subject"))
    captcha = Captcha(title=_(u"Captcha"), required=True)


class MailThatPage(silvaforms.PublicForm):

    grok.name('mailthatpage.html')
    form_fields = grok.Fields(IMailForm)

    label = _(u"Send this page by mail")

    def update(self):
        self.HEAD()

    def HEAD(self):
        self.response.setHeader(
            'Cache-Control',
            'no-cache, must-revalidate, post-check=0, pre-check=0')
        self.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
        self.response.setHeader('Pragma', 'no-cache')

    @grok.action(_(u"Send"))
    def send(self, to, subject, captcha):

        metadata = interfaces.IMetadata(self.context.get_root())
        mail_body = metadata('mail-pageactions', 'mail-body')
        mail_from = metadata('mail-pageactions', 'mail-from')

        if (not mail_from) or (not mail_body):
            self.status = _(u"Mail settings are not configured, "
                            "can't send mail at the moment.")
            return

        # UTF-8 safe
        to = to.encode('utf-8')
        subject = subject.encode('utf-8')
        mail_from = mail_from.encode('utf-8')

        url = absoluteURL(self.context, self.request)
        mail_body = mail_body % {'title': self.context.get_title(), 'url': url}
        content_type= 'application/pdf; name=%s.pdf' % self.context.getId()
        pdf = component.getMultiAdapter(
            (self.context, self.request), name="index.pdf").pdf()

        message = StringIO.StringIO()
        writer = MimeWriter.MimeWriter(message)
        writer.addheader('MIME-Version', '1.0')
        writer.addheader('Subject', subject)
        writer.addheader('To', to)
        writer.addheader('From', mail_from)
        writer.startmultipartbody('mixed')

        # start off with a text/plain part
        part = writer.nextpart()
        part.addheader('Content-Transfer-Encoding', '8bit')
        body = part.startbody('text/plain; charset="UTF-8"')
        body.write(mail_body.encode('utf-8'))

        # now add an image part
        part = writer.nextpart()
        part.addheader('Content-Transfer-Encoding', 'base64')
        body = part.startbody(content_type)
        body.write(base64.encodestring(pdf))
        writer.lastpart()

        try:
            sendmail(self.context, message.getvalue(), to, mail_from, subject)
        except SMTPException, e:
            self.status = str(e)
        else:
            exit_url = mangle.urlencode(
                url, message_status=translate(
                    _(u"Your message has been sent."), context=self.request))
            self.redirect(exit_url)


class MailPDFAction(PageAction):

    grok.order(40)

