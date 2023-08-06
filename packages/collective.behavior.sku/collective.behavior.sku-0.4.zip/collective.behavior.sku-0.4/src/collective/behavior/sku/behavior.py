from collective.behavior.sku.interfaces import ISKU
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides
from zope.interface import implements


alsoProvides(ISKU, IFormFieldProvider)


class SKU(object):
    """Behavior: SKU"""

    implements(ISKU)

    def __init__(self, context):
        self.context = context

    @property
    def sku(self):
        return getattr(self.context, 'sku', u'')

    @sku.setter
    def sku(self, value):
        """Set sku which needs to be unique.

        :param value: SKU
        :type value: unicode
        """
        if not isinstance(value, unicode):
            raise ValueError('Not Unicode')

        setattr(self.context, 'sku', value)
