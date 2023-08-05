from plone import tiles
from zope.interface import Interface

from Acquisition import aq_inner
from collective.cover import _
from collective.cover.tiles.base import AnnotationStorage
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile

from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

import time

from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from zope import schema

#from zope.component import getMultiAdapter
from plone import api 

from plone.memoize.instance import memoize
 

class IPtgTile(IPersistentCoverTile):
    """  settings for gallery  tile """
    
    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )
    
    gallerypath = schema.Choice(
        title=_(u"label_width_title_gallerytile_setting", default=u"Gallery"),
        description=_(u"label_width_description_gallerytile_setting", 
        default=u"The path to the gallery you want to  show."),
    	vocabulary='collective.ptg.tile.GalleryVocabulary',
        )

class PtgTile(PersistentCoverTile):
    implements(IPtgTile)
    index = ViewPageTemplateFile('ptg_tile.pt')
    is_configurable = True

    def is_set(self):
        return self.data['gallerypath']
        
    def gallerypath(self):
    	portal = api.portal.get() 
    	path = str(self.data['gallerypath'])
    	if path.startswith('/'):
    	    path = path[1:]
    	return portal.restrictedTraverse(path, default=False)
    	
	
	