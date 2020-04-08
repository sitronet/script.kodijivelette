#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''


'''

global Kodi
Kodi = True

global tempsdeLecture
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))


from outils import KODI_VERSION
#from outils import singleton

if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct


    ADDON = xbmcaddon.Addon()
    ADDONID = ADDON.getAddonInfo('id')
    ADDONNAME = ADDON.getAddonInfo('name')
    ADDONVERSION = ADDON.getAddonInfo('version')
    ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))

import FrameMenu

#__language__ = xbmc.Language(os.getcwd()).getLocalizedString
__settings__ = xbmcaddon.Addon(id=ADDONID)
__language__ = __settings__.getLocalizedString


def translation(message_id, default=False):
    try:
        if not __language__(message_id) and default:
            # xbmc.log('language default', xbmc.LOGNOTICE)
            xbmc.log('traduction absente : ' + str(message_id), xbmc.LOGNOTICE)
            return default
        xbmc.log('language traduit', xbmc.LOGNOTICE)
        xbmc.log(__language__(message_id), xbmc.LOGNOTICE)
        # xbmc.log(ADDON.getLocalizedString(message_id), xbmc.LOGNOTICE)
        # self.addon.getLocalizedString(message_id)
        return __language__(message_id).encode('utf-8')
        # return  ADDON.getLocalizedString(message_id).encode('utf-8')
    except:
        return __language__(message_id)


if __name__ == '__main__':

    fenetredesMenus = FrameMenu.fenetreMenu(translation(32000, 'Home'))
    fenetredesMenus.doModal()

    del fenetredesMenus

