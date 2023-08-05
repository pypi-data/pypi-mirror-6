import os.path

__version__ = '0.2'


def installdir():
    """

    Script ``smtpfixture-installdir`` to print the installation dir to help
    to start the `twistd`` daemon using an extra plugin.

    """
    print(os.path.dirname(__file__))
