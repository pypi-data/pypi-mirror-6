# -*- coding: utf-8 -*-
"""
Smtp service let the world to send email to obvious users.

usage:

twistd -no -u 1000 -g 100 smtpticket -f ../../development.ini
"""

import os
from email.Header import Header

from zope.interface import implements
from twisted.internet import protocol, defer
from twisted.mail import smtp
from twisted.mail import maildir
from twisted.python import log


class MessageStorage(object):
    """
    :class:`twisted.mail.smtp.IMessage` implementation that defer the
    implementation to Maildir.

    :param maildir: the dir path do save email
    :type maildir: str
    """
    implements(smtp.IMessage)

    def __init__(self, path):
        self.mailbox = (maildir.MaildirMailbox(path) if path != '/dev/null'
                        else None)
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        log.msg('Message data complete.')
        messageData = '\n'.join(self.lines)

        if self.mailbox:
            return self.mailbox.appendMessage(messageData)
        return defer.succeed(True)

    def connectionLost(self):
        log.msg('Connection lost unexpectedly!')
        self.lines = []


class LocalDelivery(object):
    implements(smtp.IMessageDelivery)

    def __init__(self, maildir):
        self.maildir = maildir

    def receivedHeader(self, helo, origin, recipients):
        myHostname, clientIP = helo
        headerValue = 'by %s from %s with SMTP ; %s' % (myHostname,
            clientIP, smtp.rfc822date())
        return 'Received: %s' % Header(headerValue)

    def validateFrom(self, helo, originAddress):
        self.originAddress = originAddress
        return originAddress

    def validateTo(self, user):
        log.msg('Accepting mail from %s...' % user.dest)
        return lambda: MessageStorage(self.maildir)


class SmtpFactory(protocol.ServerFactory):

    def __init__(self, maildir):
        self.maildir = maildir
        if not os.path.exists(maildir):
            os.mkdir(maildir)
        if maildir == '/dev/null':
            return
        for subdir in ('cur', 'new', 'tmp'):
            subpath = os.path.join(maildir, subdir)
            if not os.path.exists(subpath):
                os.mkdir(subpath)

    def buildProtocol(self, addr):
        log.msg('Handle new connection from %r' % addr)
        delivery = LocalDelivery(self.maildir)
        smtpProtocol = smtp.SMTP(delivery)
        smtpProtocol.factory = self
        return smtpProtocol
