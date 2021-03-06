#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''


'''

global Kodi
Kodi = True

global tempsdeLecture
import os
import sys

#sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))

if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct



# from resources.lib.outils import KODI_VERSION
#
#from outils import singleton

if Kodi:
    ADDON = xbmcaddon.Addon()
    ADDONID = ADDON.getAddonInfo('id')
    ADDONNAME = ADDON.getAddonInfo('name')
    ADDONVERSION = ADDON.getAddonInfo('version')
    ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))

from resources.lib import frameMenu
from resources.lib.outils import KODI_VERSION

#__language__ = xbmc.Language(os.getcwd()).getLocalizedString
__settings__ = xbmcaddon.Addon(id=ADDONID)
__language__ = __settings__.getLocalizedString


def translation(message_id, default=False):
    try:
        if not __language__(message_id) and default:
            xbmc.log('traduction absente : ' + str(message_id), xbmc.LOGNOTICE)
            return default
        xbmc.log('language traduit', xbmc.LOGDEBUG)
        xbmc.log(__language__(message_id), xbmc.LOGDEBUG)
        return __language__(message_id).encode('utf-8')
    except:
        return __language__(message_id)


if __name__ == '__main__':

    #fenetredesMenus = FrameMenu.fenetreMenu(translation(32001, 'Home'))
    fenetredesMenus = frameMenu.FenetreMenu()
    fenetredesMenus.doModal()
    del fenetredesMenus

