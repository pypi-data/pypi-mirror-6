
from zope.interface import Interface
from Products.Silva.ExtensionRegistry import extensionRegistry
from silva.core.conf.installer import DefaultInstaller


class IExtension(Interface):
    """Extension to send mail.
    """

METADATA = {('Silva Root', 'Silva Publication',): ('mail-pageactions',)}


class MailInstaller(DefaultInstaller):
    __name__ = 'silva.pageactions.mailpdf.install'

    def install_custom(self, root):
        self.configureMetadata(root, METADATA, globals())

    def uninstall_custom(self, root):
        self.unconfigureMetadata(root, METADATA)


install = MailInstaller('silva.pageactions.mailpdf', IExtension)

def initialize(context):
    extensionRegistry.register(
        'silva.pageactions.mailpdf', 'Send that page by mail',
        context, [], install, depends_on=('Silva', 'silva.captcha'),)
