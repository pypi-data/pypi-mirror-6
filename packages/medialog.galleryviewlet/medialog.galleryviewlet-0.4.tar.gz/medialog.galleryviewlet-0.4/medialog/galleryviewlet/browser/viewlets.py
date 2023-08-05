from Acquisition import aq_inner
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements, Interface

from plone import api

from medialog.galleryviewlet import galleryviewletMessageFactory as _
from medialog.galleryviewlet.settings import GalleryviewletSettings
from medialog.galleryviewlet.settings import IGalleryviewletSettings

class GalleryViewlet(ViewletBase):    
    implements(IGalleryviewletSettings)
    
    @property
    @memoize
    def gallerypath(self):
		context=self.context
		self.settings = GalleryviewletSettings(context)
		
		try:
			portal = api.portal.get() 
			path = str(self.settings.gallerypath)
			if path.startswith('/'):
				path = path[1:]
				
			return portal.restrictedTraverse(path, default=False)
		except:
			return False

    @property
    @memoize
    def galleryposition(self):
        context=self.context
        self.settings = GalleryviewletSettings(context)
        return self.settings.galleryposition
			