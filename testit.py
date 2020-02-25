#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Chapitre dict() voir recherchedesPlayers() avec allocation dynamique du nom des dictionnaires

Chapitre Socket : voir le fichier ConnexionClient.py

Chapitre échange de données entre Processus : main program et ConnexionClient.py
en particulier la fonction SignaAunConsommateur(), la logique adoptée ici n'est pas forcément la meilleure
mais à mon grand étonnement et bizarrement elle fonctionne
Voir aussi l'échange de donnée venant de WhereIstheServer.py :

'''


global Kodi
Kodi = True

global tempsdeLecture
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))


from outils import KODI_VERSION
from outils import singleton

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


tempsdeLecture = 1.0        # when a time.sleep(tempsdeLecture) is done to let the user read the screen. to ajust
                            # to be ergonomic or ask the user the wish timeout

class MySkin(pyxbmct.Skin):
    '''
    original source is :
    @property
    def main_bg_img(self):
        return os.path.join(self.images, 'AddonWindow', 'SKINDEFAULT.jpg')


    @property
    def background_img(self):
        return os.path.join(self.images, 'AddonWindow', 'ContentPanel.png')
    '''

    @property
    def background_img(self):
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_allegro.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_encore.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_harmony.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_nocturne.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_quartet.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_sonata.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_symphony.png'))
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_vibrato.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'fond-noir.jpg'))

    @property
    def title_background_img(self):
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_vibrato.png'))

    @property
    def main_bg_img(self):
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','fond-noir.jpg'))


pyxbmct.addonwindow.skin = MySkin()

@singleton
class Information():

    def startSqueeze(self):

        __addon__ = xbmcaddon.Addon()
        __addonname__ = __addon__.getAddonInfo('name')
        __icon__ = __addon__.getAddonInfo('icon')

        ligne_1_Information = 'Running Kodijivelette Addon Script'
        ligne_2_Information = 'Version de Kodi : ' + str(KODI_VERSION)
        ligne_3_Information =  'Addon : ' + ADDONNAME + ' ; version : ' + ADDONVERSION
        ligne_4_Information = 'Size of fixed screen : ' + str(self.screenx) + ' x ' + str(self.screeny)
        time = 5000 #in miliseconds

        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_1_Information, time, __icon__))
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_2_Information, time, __icon__))
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_3_Information, time, __icon__))
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_4_Information, time, __icon__))


if __name__ == '__main__':

    fenetredesMenus = FrameMenu.fenetreMenu('Menu')
    fenetredesMenus.doModal()
    #jivelette = SlimIsPlaying('Welcome to the most simple Squeeze Box Display : Kodi Jivelette')
    #jivelette.doModal()
    # Destroy the instance explicitly because
    # underlying xbmcgui classes are not garbage-collected on exit.


    del fenetredesMenus
    #del jivelette
