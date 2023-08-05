# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility

from silva.app.photogallery.interfaces import IPhotoGallery
from silva.app.photogallery.interfaces import IPhotoGalleryResources
from silva.core.services.interfaces import IMetadataService
from silva.core.views import views as silvaviews
from silva.fanstatic import need


class PhotoGalleryView(silvaviews.View):
    grok.context(IPhotoGallery)

    def update(self):
        need(IPhotoGalleryResources)
        self.photos = []
        self.intro = self.context.get_default()
        get_metadata = getUtility(IMetadataService).getMetadataValue

        def get_info(image):
            return {
                'title': image.get_title_or_id(),
                'url': image.url(),
                'thumbnail': image.url(thumbnail=True),
                'description': get_metadata(image, 'silva-extra', 'content_description')}

        self.photos = map(get_info, self.context.objectValues('Silva Image'))
