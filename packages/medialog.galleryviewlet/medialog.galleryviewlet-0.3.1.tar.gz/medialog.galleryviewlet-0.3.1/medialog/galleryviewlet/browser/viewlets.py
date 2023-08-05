from Acquisition import aq_inner
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements, Interface
from zope.component import getMultiAdapter

from medialog.galleryviewlet import galleryviewletMessageFactory as _
from medialog.galleryviewlet.settings import GalleryviewletSettings
from medialog.galleryviewlet.settings import IGalleryviewletSettings

class GalleryViewlet(ViewletBase):
    #render = ViewPageTemplateFile('galleryviewlet.pt')
    
    implements(IGalleryviewletSettings)
    
    @property
    @memoize
    def gallerypath(self):
		context=self.context
		self.settings = GalleryviewletSettings(context)
		
		try:
			portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
			portal = portal_state.portal()
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
			