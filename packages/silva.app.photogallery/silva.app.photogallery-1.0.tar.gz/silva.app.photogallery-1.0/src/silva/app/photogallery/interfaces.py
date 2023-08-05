# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt


from silva.core import conf as silvaconf
from silva.core.interfaces import IFolder
from silva.core.layout.interfaces import ICustomizableTag
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import js.galleriffic


class IPhotoGalleryResources(IDefaultBrowserLayer):
    silvaconf.resource(js.galleriffic.galleriffic)
    silvaconf.resource('gallery.js')
    silvaconf.resource('gallery.css')


class IPhotoGallery(ICustomizableTag):
    """Container as a photo gallery
    """
    silvaconf.only_for(IFolder)
