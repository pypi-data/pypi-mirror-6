import os.path

__version__ = '0.4'


def get_installdir():
    return os.path.dirname(__file__)


def installdir():
    """

    Script ``smtpfixture-installdir`` to print the installation dir to help
    to start the `twistd`` daemon using an extra plugin.

    """
    print(get_installdir())

