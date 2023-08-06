from zope import schema
from plone.directives import dexterity
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides
from zope.i18nmessageid import MessageFactory

from medialog.newsitemview.interfaces import INewsitemviewSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

_ = MessageFactory('medialog.newsitemviews')

def default_folderimagesize():
	settings = getUtility(IRegistry).forInterface(INewsitemviewSettings)
	return settings.default_folderimagesize

 
class ICustomSize(form.Schema):
    """ A field where you can set the size for images"""
	
    newsitemsize = schema.Choice(
        title = _("label_folderimagesize", default=u"Size for image in summary view"),
        description = _("help_folderimagesize",
                      default="Choose Size"),
        vocabulary='medialog.newsitemview.ImageSizeVocabulary',
        defaultFactory = default_folderimagesize,
    )

alsoProvides(ICustomSize, IFormFieldProvider)

