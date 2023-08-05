from Products.CMFCore.utils import getToolByName
from zope.interface import directlyProvides
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from plone import api 

from collective.plonetruegallery.interfaces import IGallery


def GalleryVocabulary(context):
    portal = api.portal.get() 
    catalog = portal.portal_catalog
    results = catalog(object_provides=IGallery.__identifier__)
    galleries= []
      
    for result in results:
        if str(result.getObject().getLayout()) == 'galleryview':
   			galleries.append(result.getPath())
   		
    terms = [ SimpleTerm(value=pair, token=pair, title=pair) for pair in galleries ]  
    return SimpleVocabulary(terms)

directlyProvides(GalleryVocabulary, IVocabularyFactory)
