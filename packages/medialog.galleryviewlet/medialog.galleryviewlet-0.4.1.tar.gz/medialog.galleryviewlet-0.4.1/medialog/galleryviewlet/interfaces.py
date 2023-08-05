from zope.interface import Interface, Attribute
from zope import schema
from medialog.galleryviewlet import galleryviewletMessageFactory  as _

class IGalleryviewletLayer(Interface):
    """
    marker interface for galleryviewlet layer
    
    """
    
class IGalleryviewlet(Interface):
    """
    marker interface for content types that can use the viewlet 
    """

    
class IGalleryviewletUtilProtected(Interface):

    def enable():
        """
        enable galleryviewlet on this object
        """

    def disable():
        """
        disable galleryviewlet on this object
        """


class IGalleryviewletUtil(Interface):

    def enabled():
        """
        checks if galleryviewlet is enabled  
        """

    def view_enabled():
        """
        checks if the galleryviewlet is selected
        """

class IGalleryviewletSettings(Interface):
    """
    The actual galleryviewlet settings
    """
     
    gallerypath = schema.Choice(
        title=_(u"label_galleryviewlet_setting", default=u"Gallery"),
        description=_(u"label_galleryviewlet_setting",
        default=u"The path to the gallery you want to  show."),
        vocabulary='medialog.galleryviewlet.GalleryVocabulary',
        )

    galleryposition = schema.Bool(
        title=_(u"label_position_galleryviewlet_setting", default=u"Below Content?"),
        description=_(u"label_position_galleryviewlet_setting",
        default=u""),
        required=False)