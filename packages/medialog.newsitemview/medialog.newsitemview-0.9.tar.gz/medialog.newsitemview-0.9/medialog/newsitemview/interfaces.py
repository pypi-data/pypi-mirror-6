from z3c.form import interfaces
from zope import schema
from zope.interface import Interface
from zope.interface import alsoProvides
from plone.directives import form
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
from medialog.newsitemview.vocabulary import ImageSizeVocabulary
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('medialog.newsitemview')


class INewsitemviewSettings(form.Schema):
    """Adds settings to medialog.controlpanel
    """

    form.fieldset(
        'newsitemview',
        label=_(u'Newsitemview Settings'),
        fields=[
            'default_folderimagesize',
            'default_newsitemsize',
            'default_hideimages',
            ],
        )
    
    default_folderimagesize = schema.Choice(
    	title=_(u"default_folderimagesize", default=u"Default Folderimage Size"),
    	vocabulary = 'medialog.newsitemview.ImageSizeVocabulary',
    	required = True,
    	description=_(u"help_default_folderimagesize",
    		default=u"Set default size for Folderimage")
    	)

    default_newsitemsize = schema.Choice(
    	required = True,
    	vocabulary = 'medialog.newsitemview.ImageSizeVocabulary',
    	title=_(u"default_newsimagesize", default=u"Default Newsimage Size"),
    	description=_(u"help_default_newsimagesize",
                      default=u"Set default size for Newsimage")
    )

    default_hideimages = schema.Bool(
    	title=_(u"default_hideimages", default=u"Hide images in folder view by default"),
    	description=_(u"help_default_hideimages",
                      default=u"Set if images should be hidden folder view")
    )


alsoProvides(INewsitemviewSettings, IMedialogControlpanelSettingsProvider)



    
class INewsitemObject(Interface):
    """Marker interface for marking an object"""
    
class IFolderObject(Interface):
    """Marker interface for marking a folder"""
    