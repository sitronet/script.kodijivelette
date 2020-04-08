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




if __name__ == '__main__':

    fenetredesMenus = FrameMenu.fenetreMenu('Menu')
    fenetredesMenus.doModal()
    #jivelette = SlimIsPlaying('Welcome to the most simple Squeeze Box Display : Kodi Jivelette')
    #jivelette.doModal()
    # Destroy the instance explicitly because
    # underlying xbmcgui classes are not garbage-collected on exit.


    del fenetredesMenus
    #del jivelette
