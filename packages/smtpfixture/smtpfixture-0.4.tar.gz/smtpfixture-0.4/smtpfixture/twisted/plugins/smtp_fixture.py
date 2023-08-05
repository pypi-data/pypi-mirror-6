#-*- coding: utf-8 -*-
"""
:mod:`smtpfixture.twisted.plugins.smtp_server`
==============================================

plugin for the twistd deamon that create the smtp server.

"""

import os.path
from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet


class Options(usage.Options):
    """
    Config parser for the twisted plugin.
    """
    optParameters = [['port', 'p', 8025, 'Port to listen'],
                     ['interface', 'i', '0.0.0.0', 'Interface to listen'],
                     ['maildir', 'm', '~/Maildir',
                      'Directory where mail will be stored or '
                      '/dev/null for blackhole usage']
                     ]


class SmtpFixtureServiceMaker(object):
    """
    Implements :class:`twisted.plugin.IPlugin` and
    :class:`twisted.application.service.IServiceMaker` to create a
    smtp server using twisted plugin configured with a paste ini file.
    """

    implements(IServiceMaker, IPlugin)
    tapname = 'smtpfixture'
    description = 'Store email in localdir using maildir format'
    options = Options

    def makeService(self, options):
        """
        Create the smtp server configured with the given option.

        :return: the smtp server instance.
        :rtype: :class:`twisted.application.internet.TCPServer`
        """

        from smtpfixture.smtp import SmtpFactory
        maildir = os.path.expanduser(options['maildir'])
        return internet.TCPServer(int(options['port']),
                                  SmtpFactory(maildir=maildir),
                                  interface=options['interface'])

serviceMaker = SmtpFixtureServiceMaker()
