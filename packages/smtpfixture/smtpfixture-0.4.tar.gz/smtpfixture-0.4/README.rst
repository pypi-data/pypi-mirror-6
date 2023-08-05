smtpfixture
===========

Run a smtp server that store every mail in a Maildir_.
The goal is to tests that emails are sent when doing functional tests.
You can also use it to verify the rendering of email in a desktop email client,
that real Maildir format.
You can also use it has a smtp server blackhole or test that you do not
send email.

.. _Maildir: http://en.wikipedia.org/wiki/Maildir


smtpfixture is based on twisted and is just few line of codes for writing a
TAP file.

Installation
------------

::

    pip install smtpfixture


usage
-----

::

    cd `smtpfixture-installdir` && twistd smtpfixture


.. note::

    smtpfixture is a tap file and it must be found by the twistd script.
    To get the plugin discovered by twistd, a change directory must be done.
    if you have a better solution, just let me now.

To stop the service, you can run the following command:

::

    kill `cat twistd.pid`


.. note::

    The command ``twistd -n smtpfixture`` can be used to avoid deamonization.

By default smtpfixture run on port 8025 as it did not require any privileges,
but you can run it on the port you want.

To run it on port 25, as root, as a smtp blackhole (no email stored):

::

    cd `smtpfixture-installdir` && twistd smtpfixture -p 25 -m /dev/null


.. note::

    twistd provide options to change the uid/gid to fix privileges issues.

