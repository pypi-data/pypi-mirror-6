#from zope import schema
from zope.interface import alsoProvides
from zope.i18nmessageid import MessageFactory
from medialog.qrcode.interfaces import IqrcodeLayer
from zope.interface import Interface

_ = MessageFactory('medialog.qrcode')
 
class IQRbehavior(Interface):
    """ shows a viewlet with the qrcode 
         useful for pdf templates and printing
     """
    pass


alsoProvides(IQRbehavior, IqrcodeLayer)

