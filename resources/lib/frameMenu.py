#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

'''


global Kodi
Kodi = True

global savepath  # à revoir
global tempsdeLecture

import platform
import os
import sys
import urllib
import random
import threading
import time
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))

#from outils import WhereIsTheLMSServer
from resources.lib.connexionClient import InterfaceCLIduLMS
from resources.lib.outils import KODI_VERSION
from resources.lib.ecoute import Souscription
from resources.lib import ecoute, framePlaying, framePlaylist, outils, plugin
import json
#from singleton_decorator import singleton

from resources.lib import pyxbmctExtended

if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct

    DEBUG_LEVEL = xbmc.LOGDEBUG
    from  resources.lib.outils import debug


    ADDON = xbmcaddon.Addon()
    ADDONID = ADDON.getAddonInfo('id')
    ADDONNAME = ADDON.getAddonInfo('name')
    ADDONVERSION = ADDON.getAddonInfo('version')
    ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))

    #__language__ = xbmc.Language(os.getcwd()).getLocalizedString
    __settings__ = xbmcaddon.Addon(id=ADDONID)
    __language__ = __settings__.getLocalizedString

    # print __language__(32001)

    TIME_OF_LOOP_SUBSCRIBE = ecoute.TIME_OF_LOOP_SUBSCRIBE

    # screen 16:9 so to have grid square fix to 16-9 on 1280 x 720 max of pyxbmct
    SIZE_WIDTH_pyxbmct = 1280
    SIZE_HEIGHT_pyxbmct = 720
    SEIZE = 16 * 4  #32 16 option so 64
    NEUF =   9 * 4  #18 or 9      so 36

    #savepath = '/tmp/'
    savepath = xbmc.translatePath('special://temp')

    def translation(message_id, default=False):

        try:
            if not __language__(message_id) and default:
                #debug('language default', xbmc.LOGNOTICE)
                debug( 'traduction absente : ' + str(message_id) , xbmc.LOGNOTICE)
                return default
            debug('language traduit', xbmc.LOGDEBUG)
            debug( __language__(message_id), xbmc.LOGNOTICE)
            #debug(ADDON.getLocalizedString(message_id), xbmc.LOGNOTICE)
            #self.addon.getLocalizedString(message_id)
            return __language__(message_id).encode('utf-8')
            #return  ADDON.getLocalizedString(message_id).encode('utf-8')
        except:
            return __language__(message_id)

tempsdeLecture = 1.0        # when a time.sleep(tempsdeLecture) is done to let the user read the screen. to ajust
                            # to be ergonomic or ask the user the wish timeout

# Kodi key action codes.
# More codes available in xbmcgui module
ACTION_PREVIOUS_MENU = 10
"""ESC action"""
ACTION_NAV_BACK = 92
"""Backspace action"""
ACTION_MOVE_LEFT = 1
"""Left arrow key"""
ACTION_MOVE_RIGHT = 2
"""Right arrow key"""
ACTION_MOVE_UP = 3
"""Up arrow key"""
ACTION_MOVE_DOWN = 4
"""Down arrow key"""
ACTION_MOUSE_WHEEL_UP = 104
"""Mouse wheel up"""
ACTION_MOUSE_WHEEL_DOWN = 105
"""Mouse wheel down"""
ACTION_MOUSE_DRAG = 106
"""Mouse drag"""
ACTION_MOUSE_MOVE = 107
"""Mouse move"""
ACTION_MOUSE_LEFT_CLICK = 100
"""Mouse click"""

ACTION_CONTEXT_MENU = 117
'''for my webchip remote'''
ACTION_FORWARD = 16
ACTION_REWIND = 17
ACTION_MUTE = 91
ACTION_NEXT_ITEM = 14
ACTION_PAUSE = 12
ACTION_PLAY = 68
ACTION_PLAYER_FORWARD = 77
ACTION_PLAYER_PLAY = 79
ACTION_PLAYER_PLAYPAUSE = 229
ACTION_PLAYER_REWIND = 78
ACTION_PREV_CONTROL = 182
ACTION_PREV_ITEM = 15
ACTION_PREV_LETTER = 141
ACTION_PREV_PICTURE = 29
ACTION_PREV_SCENE = 139
ACTION_SHOW_FULLSCREEN = 36
ACTION_SHOW_GUI = 18
ACTION_SHOW_INFO = 11
ACTION_SHOW_MPLAYER_OSD = 83
ACTION_SHOW_OSD = 24
ACTION_SHOW_OSD_TIME = 123
ACTION_SHOW_PLAYLIST = 33
ACTION_SMALL_STEP_BACK = 76
ACTION_STEP_BACK = 21
ACTION_STEP_FORWARD = 20
ACTION_STOP = 13
ACTION_SWITCH_PLAYER = 234
ACTION_VOLAMP_DOWN = 94
ACTION_VOLAMP_UP = 93
ACTION_VOLUME_DOWN = 89
ACTION_VOLUME_UP = 88


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
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_vibrato.png'))


pyxbmct.addonwindow.skin = MySkin()


# todo : test , try to catch the requete from frameList (communicate between frame) , is it possible ?

# Then create your UI window class with the new background
#class MyCoolWindow(pyxbmct.AddonWindow):

def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

#@singleton
#class FenetreMenu(pyxbmct.AddonFullWindow):    # background (skin) header+ title
#class FenetreMenu(pyxbmct.AddonDialogWindow):  # background (skin) header+ title + on the top screen
#class FenetreMenu(pyxbmct.BlankDialogWindow):  # transparent without header+title and on top
#class FenetreMenu(pyxbmct.BlankFullWindow):    # black background without header+title (cannot change background)
#class FenetreMenu(pyxbmctExtended.AddonFullWindowWT)  # background (skin) without header+title
class FenetreMenu(pyxbmct.AddonFullWindow):

    def __init__(self,*args, **kwargs):
        #title = args[0]
        super(FenetreMenu, self).__init__()

        self.Window_is_playing  = xbmcgui.getCurrentWindowId()
        self.flagContextMenu = False
        self.flagVolumeDisplay = False
        self.flagStatePause = False
        self.recevoirEnAttente= threading.Event()
        self.recevoirEnAttente.clear()
        self.demandedeStop = threading.Event()
        self.demandedeStop.clear()
        self.envoiEnAttente = threading.Event()
        self.envoiEnAttente.clear()  # initialisation ok
        # pour l'abonnement en subscribe :
        self.Abonnement = threading.Event()
        self.Abonnement.set()  # etrange erreur à l'execution
        # take care : When abonnement is set the flag is True and don't block the external thread subscribe
        #            When abonnement is clear the flag is False and must block the thread subscribe
        debug('entry in : ' + self.__class__.__name__  + ' ' +  sys._getframe().f_code.co_name , xbmc.LOGNOTICE)
        debug('Starting Frame for the menu  with window  pyxbmct , ' + str(self.Window_is_playing) , xbmc.LOGNOTICE)
        debug('special temp is : ' + str(savepath) , xbmc.LOGNOTICE )

        self.image_dir = ARTWORK    # path to pictures used in the program

        self.startSqueeze()
        self.testEnvironnement()        # just to know a few things about the system (not necessary for the continuation)

        self.geometrie()                # set the geometrie of screen
        self.defineControlMenus()       # definition of all the elements on the screen (list, button...)
        self.putControlElements()       # placement of all elements on the screen -mainly placeControl(List, Button...
        self.welcome()                  # just a welcome message
        self.set_navigation_lateral()   # defined menu navigation (menu left <-> submenu right)
        self.connexionEvent()           # defined Actions when some key is pressed (example : right, left, down, up arrow)
        self.population()               # initialization of flags on the menus (is it still necessary ?)

        self.backgroundFonction()       # TODO : should be deleted, should be replaced with window calls, or calls to panes

        self.connectControlElements()   # For each menu defines the function called when an item is selected in the menu
        self.setFocus(self.listMenu_Initialisation_server)  # the entry point for the program began

        debug('FIN de _init_', xbmc.LOGDEBUG)


    def onAction(self, action):
        """
        Catch button actions.

        ``action`` is an instance of :class:`xbmcgui.Action` class.
        """
        self.WindowPlaying_current = xbmcgui.getCurrentWindowId()
        debug('fenetre en sortie dans methode onAction n° : ' + str(self.WindowPlaying_current), xbmc.LOGDEBUG)
        debug('fenetre enregistrée dans methode now_is_playing n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        if action == ACTION_PREVIOUS_MENU:
            # todo : à redéfinir si au milieu des menus
            # pour ne pas sortir
            # sortir uniquement si menu racine ou init
            debug('Action Previous_menu' , xbmc.LOGNOTICE)
            self.quit()

        elif action == ACTION_NAV_BACK:
            debug('Action nav_back' , xbmc.LOGNOTICE)
            self.quit()

        elif action == xbmcgui.ACTION_CONTEXT_MENU:     # it's a strange icon key on my remote
            debug('Action ContextMenu', xbmc.LOGNOTICE)
            self.flagContextMenu = True
            self.promptContextMenu()

        elif action == ACTION_PAUSE:  # currently it's the space bar on my remote
            debug('Action Pause', xbmc.LOGNOTICE)
            self.pause_play()

        elif action == ACTION_PLAY or action == ACTION_PLAYER_PLAY:
            debug('Action Play', xbmc.LOGNOTICE)
            self.pause_play()

        elif action == ACTION_VOLUME_UP:    # it's the volume key Vol+  on my remote
            self.promptVolume()

        elif action == ACTION_VOLUME_DOWN:  # it's the volume key Vol-  on my remote
            self.promptVolume()


        else:
            debug('else condition onAction in frameMenu' + str(action)  , xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)

    def quit(self):
        debug('quit asked - Exit program  0 fonction quit() .', xbmc.LOGNOTICE)
        line1 = " Do you want to exit this script ? "
        Acknownledge = xbmcgui.Dialog().yesno('Exit KodiJivelette', line1)
        if Acknownledge:
            self.Abonnement.clear()
            time.sleep(0.2)
            self.demandedeStop.set()
            try:
                self.InterfaceCLI.closeconnexionWithCLI()
                time.sleep(0.2)
                del self.InterfaceCLI
            except AttributeError:
                pass
            debug('quit done - Exit program  0 fonction quit() .', xbmc.LOGNOTICE)
            self.close()
        else:
            pass

    #def onControl(self, control):
    #    debug("Window.onControl(control=[%s])"%control , xbmc.LOGNOTICE)

    def desabonner(self):
        '''not used but in case we need '''
        self.breakBoucle_A = True
        self.Abonnement.clear()

    def startSqueeze(self):
        ''' only a dialog popup to notify the begining of the program'''
        __addon__ = xbmcaddon.Addon()
        __addonname__ = __addon__.getAddonInfo('name')
        __icon__ = __addon__.getAddonInfo('icon')

        ligne_1_Information = translation(32010, default='Running Kodijivelette Addon Script')
        ligne_2_Information = translation((32020), default='Version de Kodi : ') + str(KODI_VERSION)
        ligne_3_Information =  translation(32030, default='Addon : ') + ADDONNAME + ' ; ' + translation(32040, default= 'Version : ') + ADDONVERSION
        # don't have this information at this time :
        #ligne_4_Information = 'Size of fixed screen : ' + str(self.screenx) + ' x ' + str(self.screeny)
        time = 5000 #in miliseconds

        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_1_Information, time, __icon__))
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_2_Information, time, __icon__))
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_3_Information, time, __icon__))
        #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDONNAME,ligne_4_Information, time, __icon__))


    def testEnvironnement(self):
        ''' just to log platform, system ...'''
        debug('path : ' + str(sys.path) , xbmc.LOGNOTICE)
        debug('test environnement : ' + str(os.tmpfile()) + ' - '+ str(os.uname()) , xbmc.LOGNOTICE)
        leSystem = platform.system()
        debug( 'System : ' + str(leSystem) , xbmc.LOGNOTICE )
        laplateforme = platform.platform()
        debug('System more : '+ str(laplateforme),xbmc.LOGNOTICE)

    def geometrie(self):
        '''set the geometry of the screen (main Window of the script, point of entry )
        to place later elements and controls (list button image etc...)'''
        SIZESCREEN_HEIGHT = xbmcgui.getScreenHeight()            # exemple  # 1080
        SIZESCREEN_WIDTH = xbmcgui.getScreenWidth()                         # 1920

        # I didn't know the operator '//' when I wrote this code
        self.GRIDSCREEN_Y, Reste = divmod(SIZESCREEN_HEIGHT, 10)            # 108
        self.GRIDSCREEN_X, Reste = divmod(SIZESCREEN_WIDTH, 10)             # 192

        self.screenx = SIZESCREEN_WIDTH
        self.screeny = SIZESCREEN_HEIGHT
        debug('Size of Frame Menu: ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        if self.screenx > SIZE_WIDTH_pyxbmct:
            self.screenx = SIZE_WIDTH_pyxbmct
            self.screeny = SIZE_HEIGHT_pyxbmct
        #pyxbmct :
        self.setGeometry(width_=self.screenx, height_=self.screeny, rows_=NEUF, columns_=SEIZE)
        debug('Size of Frame Menu fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        # size of the cover must be  a square
        #SIZECOVER_X  = int(self.GRIDSCREEN_X * 2.5)  # need to ask artWork size from server, adapt to the size screen
        SIZECOVER_X = int(self.screenx / SEIZE * 28 )
        self.sizecover_x = SIZECOVER_X          # 1720 / 64 * 28 = 560 pixels
        #SIZECOVER_Y = self.GRIDSCREEN_Y * 3  # and reserve a sized frame to covers,attention SIZECOVER_X != SIZECOVER_Y
        debug('Taille pochette : ' + str(SIZECOVER_X) + ' x ' + str(SIZECOVER_X) , xbmc.LOGNOTICE)

        self.image_dir = ARTWORK    # path to pictures used in the program (future development)

        self.cover_jpg = self.image_dir + '/music.png'      # pour le démarrage then updated
        self.image_background = self.image_dir + '/fond-noir.jpg'  # in next release could be change by users
        self.image_progress = self.image_dir + '/ajax-loader-bar.gif'   # not yet used, get from speedtest
        self.image_button_pause = self.image_dir + '/pause.png'   # get from Xsqueeze
        self.image_button_stop = self.image_dir + '/stop.png'     # get from Xsqueeze
        self.image_button_play = self.image_dir + '/play.png'     # get from Xsqueeze
        self.textureback_slider_duration = self.image_dir + '/slider_back.png'  # get from plugin audio spotify
        self.texture_slider_duration = self.image_dir + '/slider_button_new.png'
        self.image_list_focus = self.image_dir + '/MenuItemFO.png'        # get from myself
        self.textureback_slider_volume = self.image_dir + '/slider_back.png'
        self.texture_slider_volume = self.image_dir + '/slider_button_new.png'

        # for icon on the root menu :
        self.image_dir_root_menu = self.image_dir + '/Slimserver'
        self.image_radio_root = self.image_dir_root_menu + '/radio.png'
        self.image_app_root = self.image_dir_root_menu + '/icon_app.png'
        self.image_favorites_root = self.image_dir_root_menu + '/icon_favorites.png'

        self.image_mymusic_root = self.image_dir_root_menu + '/squeezecenter.png'



    def backgroundFonction(self):

        # button pause :
        self.bouton_pause = pyxbmct.Button(label='', focusTexture=self.image_button_pause,
                                           noFocusTexture=self.image_button_pause)
        self.placeControl(control=self.bouton_pause, row=NEUF / 2, column=int(SEIZE / 2) - 5, rowspan=6, columnspan=6)
        self.bouton_pause.setVisible(False)
        self.bouton_play = pyxbmct.Button(label='', focusTexture=self.image_button_play, noFocusTexture='')
        self.placeControl(self.bouton_play, row=NEUF / 2, column=(SEIZE / 2) - 2, rowspan=6, columnspan=6)
        self.bouton_play.setVisible(False)

    def defineControlMenus(self):
        ''' Fix the size of itemlists in menus lists'''

        self.ListePourInitialisationServer = [ translation(32920 , 'Init the Server' ),
                                                      translation(32921 , 'Quit the program' )]

        #self.ListePourInitialisationPlayers = []

        self.listeRacinePourMenuRacine = [ translation(32040 , 'Now Playing'),
                                           translation(32041 , 'My Music'),
                                           translation(32042 , 'I-Radio' ),
                                           translation(32043 , 'My Apps'),
                                           translation(32044 , 'Favorites'),
                                           translation(32045 , 'Extras'),
                                           translation(32046 , 'Quit') ]

        #self.listeMyMusicPourMenuMyMusic = [
        #                                translation(32050 , 'Album Artists'),
        #                                translation(32051 , 'All Artists'),
        #                                translation(32052 , 'Composers'),
        #                                translation(32053 , 'Albums'),
        #                                translation(32054 , 'Compilations'),
        #                                translation(32055 , 'Genres'),
        #                                translation(32056 , 'Years'),
        #                                translation(32057 , 'New Music'),
        #                                translation(32058 , 'Random Mix'),
        #                                translation(32059 , 'Music Folder'),
        #                                translation(32060 , 'Playlists'),
        #                                translation(32061 , 'Search'),
        #                                translation(32062 , 'Remote Music Librairies') ]

        self.listeMyMusicPourMenuMyMusic = [
            translation(32050, 'Album Artists'),
            translation(32051, 'All Artists'),
            translation(32052, 'TODO'),
            translation(32053, 'Albums'),
            translation(32054, 'TODO'),
            translation(32055, 'TODO'),
            translation(32056, 'TODO'),
            translation(32057, 'TODO'),
            translation(32058, 'Random Mix'),
            translation(32059, 'Music Folder'),
            translation(32060, 'TODO'),
            translation(32061, 'TODO'),
            translation(32062, 'TODO')]

        #self.listeExtraPourMenuExtras = [ translation(32072 , 'players'),
        #                                  translation(32073 , 'Music Source') ,
        #                                  translation(32074 , 'Don\'t stop the music') ]

        self.listeExtraPourMenuExtras = [translation(32072, 'players'),
                                         translation(32073, 'TODO'),
                                         translation(32074, 'TODO')]

        self.listMenu_Initialisation_server = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _itemHeight=40)

        self.listMenu_Initialisation_players = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _itemHeight=40)

        self.listMenu_Racine = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 40 , _imageHeight = 40 , _itemHeight=40)

        self.listMenu_MyMusic = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 38 , _imageHeight = 38 , _itemHeight = 40 )

        self.listMenu_Branches  = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 38 , _imageHeight = 38 , _itemHeight = 40 )

        # we keep it for later (settings and so)
        self.listMenu_Extras = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)

        # à voir plus tard
        self.listMenu_Feuilles = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_all_Artists = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_all_Albums = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_ArtistAlbums = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_all_Dossiers = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_RandomMix= pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_Extras= pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)

        #todo
        self.listMenu_Fleur = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)

    def putControlElements(self):
        ''' mainly place the menus lists on the screen
        this is more to have a global view readable of the screen than the need to code it
        in fact each is removed and added according to the positioning in the menu in the function
        list_Menu_Navigation(self):
        '''

        ligneLabel= NEUF - 1
        #label pour indiquer les items sélectionnés dans la hiérarchie des menus, permet aussi de tester la navigation
        self.list_racine_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.list_racine_label, ligneLabel, 2, 1 , 10)

        self.list_item_branche_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.list_item_branche_label, ligneLabel, 12, 1 , 10)

        self.list_item_feuille_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.list_item_feuille_label, ligneLabel, 22, 1, 12)

        self.list_item_fleur_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.list_item_fleur_label, ligneLabel, 34, 1, 20)

        self.Information_label = pyxbmct.Label('', textColor='0xFF808888')
        self.placeControl(self.Information_label, (NEUF / 2) - 5 , ( SEIZE / 2 )- 10 , 1 , 20  )


        self.row_depart = 1
        self.espace_row = 30
        self.espace_col = 18
        self.col_depart_menu_branche = self.espace_col + 1
        self.row_hauteur_menu_branche = 30
        self.col_largeur_menu_branche = 18
        self.col_depart_menu_feuille = self.col_depart_menu_branche + self.col_largeur_menu_branche
        self.col_largeur_menu_feuille = self.col_largeur_menu_branche + 10
        self.row_hauteur_menu_feuille = self.row_hauteur_menu_branche

        # init
        
        self.placeControl(self.listMenu_Initialisation_server,
                          NEUF // 2  ,
                          (SEIZE // 2 ) - self.espace_col //2 ,
                          self.espace_row,
                          self.espace_col  )

        self.placeControl(self.listMenu_Initialisation_players,
                          NEUF // 2,
                          (SEIZE // 2) - self.espace_col // 2 ,
                          self.espace_row,
                          self.espace_col )

        self.placeControl(self.listMenu_Racine ,
                          self.row_depart ,
                          0,
                          self.espace_row,
                          self.espace_col)

        # Add items to the list
        self.listMenu_Initialisation_server.addItems(self.ListePourInitialisationServer)
        self.listMenu_Racine.addItems(self.listeRacinePourMenuRacine)
        itemroot = self.listMenu_Racine.getListItem(1)
        itemroot.setArt({'thumb': self.image_mymusic_root })
        itemroot = self.listMenu_Racine.getListItem(2)
        itemroot.setArt({'icon': self.image_radio_root })
        itemroot = self.listMenu_Racine.getListItem(3)
        itemroot.setArt({'icon': self.image_app_root})
        itemroot = self.listMenu_Racine.getListItem(4)
        itemroot.setArt({'icon': self.image_favorites_root})

        self.listMenu_Extras.addItems(self.listeExtraPourMenuExtras)

        # I try to paste the control here if not raise un error
        self.placeControl(self.listMenu_MyMusic,
                          self.row_depart,
                          self.col_depart_menu_branche,
                          self.row_hauteur_menu_branche,
                          self.col_largeur_menu_branche)

        self.placeControl(self.listMenu_Branches , self.row_depart, self.col_depart_menu_branche, \
                          self.row_hauteur_menu_branche, self.col_largeur_menu_branche)

        self.placeControl(self.listMenu_Extras, self.row_depart , self.col_depart_menu_branche, \
                          self.row_hauteur_menu_branche, self.col_largeur_menu_branche)

        self.placeControl(self.listMenu_Feuilles, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_feuille,self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_all_Artists, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_branche,self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_all_Albums, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_branche, self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_ArtistAlbums, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_branche, self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_all_Dossiers, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_branche, self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_RandomMix, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_branche,self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_Extras, self.row_depart, self.col_depart_menu_feuille, \
                          self.row_hauteur_menu_branche,self.col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Fleur, self.row_depart , self.col_depart_menu_feuille + self.col_largeur_menu_branche  , \
                          self.row_hauteur_menu_branche , self.col_largeur_menu_branche )


    def connectControlElements(self):
        # Connect the list to a function to display which list item is selected.
        # example :
        # self.connect(self.list_Menu, lambda: xbmc.executebuiltin('Notification(Note!,{0} selected.)'.format(
        #    self.list_Menu.getListItem(self.list_Menu.getSelectedPosition()).getLabel())))

        # init
        self.connect(self.listMenu_Initialisation_server, self.navigationFromMenuInitialisationServer)
        self.connect(self.listMenu_Initialisation_players, self.navigationFromMenuPlayers)
        #
        self.connect(self.listMenu_Racine, self.navigationFromMenuRacine)
        self.connect(self.listMenu_MyMusic, self.navigationFromMenusMyMusic)
        self.connect(self.listMenu_Branches, self.navigationFromMenuBranche)
        self.connect(self.listMenu_Feuilles, self.navigationFromMenuFeuilles)
        self.connect(self.listMenu_Feuilles_ArtistAlbums, self.navigationFromMenuFeuilles_ArtistAlbums)
        self.connect(self.listMenu_Feuilles_all_Artists, self.navigationFromMenuFeuilles_all_Artists)
        self.connect(self.listMenu_Feuilles_all_Albums, self.navigationFromMenuFeuilles_all_Albums)
        self.connect(self.listMenu_Feuilles_all_Dossiers, self.navigationFromMenuFeuilles_all_Dossiers)
        self.connect(self.listMenu_Feuilles_RandomMix, self.navigationFromMenuFeuilles_RandomMix)
        self.connect(self.listMenu_Extras, self.navigationFromMenuBrancheExtras)
        self.connect(self.listMenu_Feuilles_Extras, self.navigationFromMenuFeuillesExtras)

        self.connect(self.listMenu_Fleur, self.launchPlayingItem)
        # etcoetera...
        #

    def connexionEvent(self):
        # Connect key and mouse events for list navigation feedback.
        self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_UP,
             pyxbmct.ACTION_MOUSE_MOVE,
             pyxbmct.ACTION_MOVE_LEFT,
             pyxbmct.ACTION_MOVE_RIGHT],
            self.list_Menu_Navigation)

    def population(self):
        # todo dois je créer toutes les sous-listes ici ? ou bien attendre dans le menu
        # do we need this later ? let's see .
        self.music_branch_populated = False
        self.radios_populated = False
        self.apps_populated = False
        self.Favorites_populated = False
        self.Extras_populated = False
        self.all_Artists_populated = False
        self.all_albums_populated = False
        self.all_dossiers_populated = False
        self.ArtistAlbums_populated = False

    def set_navigation_lateral(self):

        # Set navigation between controls (Button, list or slider) on the side (Right-Left) of Elements
        # don't need in this screen above and below (Up and Down)
        # Control has to be added to a window first if not raise RuntimeError

        #this behavior could change during the programm to get My_Music and Extras if need
        self.listMenu_Racine.controlRight(self.listMenu_Branches)

        # these are statics till the end
        self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
        self.listMenu_Branches.controlLeft(self.listMenu_Racine)
        self.listMenu_Extras.controlLeft(self.listMenu_Racine)

        self.listMenu_Branches.controlRight(self.listMenu_Feuilles)
        self.listMenu_Feuilles.controlLeft(self.listMenu_Branches)
        self.listMenu_Feuilles_all_Artists.controlLeft(self.listMenu_MyMusic)
        self.listMenu_Feuilles_all_Albums.controlLeft(self.listMenu_MyMusic)
        self.listMenu_Feuilles_ArtistAlbums.controlLeft(self.listMenu_MyMusic)
        self.listMenu_Feuilles_all_Dossiers.controlLeft(self.listMenu_MyMusic)
        self.listMenu_Feuilles_RandomMix.controlLeft(self.listMenu_MyMusic)

        self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)
        self.listMenu_Feuilles_Extras.controlLeft(self.listMenu_Extras)

        self.listMenu_Feuilles.controlRight(self.listMenu_Fleur)
        self.listMenu_Fleur.controlLeft(self.listMenu_Feuilles)

        # todo : à revoir pour les autre menus (radios , favorites etc...

        # Set initial focus
        #self.setFocus(self.listMenu_Racine)


    def move_through_sub_menu(self):
        # on verra plus tard si nécessaire Todo When action move left, right and previous menu or back
        self.itemSelectionRacine = self.list_Menu.getListItem(self.list_Menu.getSelectedPosition()).getLabel()

    def launchPlayingNowandOthersCommands(self, title):
        '''
        :param title:
        :return:
        '''
        #itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

        self.Abonnement.set()
        # With AddonFullWindow
        #self.jivelette = framePlaying.SlimIsPlaying(title)
        # With BlankAddonWindow (no title)
        self.jivelette = framePlaying.SlimIsPlaying()
        # todo test show() or doModal()
        # with show the update is here
        # with doModal the update is in jivelette
        #self.jivelette.show()
        #self.update_now_is_playing()
        self.jivelette.doModal()
        del self.jivelette

    def launchPlayingItem(self):
        ''' when an app or a radio is selected  launch the command to play
        mainly : cmd playlist play item_id
        example : radioparadise playlist play item_id:25478.1
        we guess that we are in the menu Flower, but not always true Todo extends to others menus
        '''
        labelajouer = self.listMenu_Fleur.getListItem(self.listMenu_Fleur.getSelectedPosition()).getLabel()
        # set the label on the bottom of screen
        self.list_item_fleur_label.setLabel(labelajouer)
        cmd = self.listMenu_Feuilles.getListItem(self.listMenu_Feuilles.getSelectedPosition()).getProperty('cmd')
        #cmd ='picks' ,  ....Radio, shoutcast ...
        item_id = self.listMenu_Fleur.getListItem(self.listMenu_Fleur.getSelectedPosition()).getProperty('id')
        audio_type = self.listMenu_Fleur.getListItem(self.listMenu_Fleur.getSelectedPosition()).getProperty('type')
        hasitems = self.listMenu_Fleur.getListItem(self.listMenu_Fleur.getSelectedPosition()).getProperty('hasitems')

        debug('launch to play : ' + labelajouer + ' ' + cmd + ' playlist play item_id:' + item_id , xbmc.LOGNOTICE  )
        if audio_type == 'audio' and hasitems == '0':
            # send the command to play the item_id
            self.InterfaceCLI.viderLeBuffer()
            self.InterfaceCLI.sendtoCLISomething( cmd + ' playlist play item_id:' + item_id )
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            time.sleep(0.5) # let's the time to retrieve the stream to get the cover
            # then launch the frame Now_is_playing
            # self.command here become the title of the Frame
            if  '|local|playlist|play|item_id:' in reponse:
                self.launchPlayingNowandOthersCommands(labelajouer)

        else:
            outils.functionNotYetImplemented()


    def navigationFromMenuInitialisationServer(self):
        # is this below necessary ?
        try:
                self.listMenu_Initialisation_server.setVisible(True)
                self.listMenu_Initialisation_players.setVisible(False)

                self.listMenu_Racine.setVisible(False)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
        except:
                pass

        self.setFocus(self.listMenu_Initialisation_server)
        itemSelection = self.listMenu_Initialisation_server.getListItem(self.listMenu_Initialisation_server.getSelectedPosition()).getLabel()
        itemPosition = self.listMenu_Initialisation_server.getSelectedPosition()
        debug('item server selected is : ' + str(itemSelection), xbmc.LOGNOTICE)
        if itemSelection ==  translation(32920 , 'Init the Server'):
            self.initialisationServeur()
            self.listMenu_Initialisation_server.setVisible(False)
            self.removeControl(self.listMenu_Initialisation_server)
            self.initialisationPlayeur()

            #self.selectPlayer()
            self.testCapaciteServeur()
            self.set_artwork_size()
            #self.listMenu_Initialisation_server.setVisible(False)
            #self.removeControl(self.listMenu_Initialisation_server)
            #self.getFocus(self.listMenu_Racine)

        elif itemSelection == translation(32921 , 'Quit the program' ):
            self.quit()

        else :
            pass


    def navigationFromMenuPlayers(self):
        try:
            self.listMenu_Initialisation_server.setVisible(False)
            self.listMenu_Initialisation_players.setVisible(True)

            self.listMenu_Racine.setVisible(False)
            self.listMenu_MyMusic.setVisible(False)
            self.listMenu_Branches.setVisible(False)
            self.listMenu_Extras.setVisible(False)
            self.listMenu_Feuilles.setVisible(False)
            self.listMenu_Feuilles_all_Artists.setVisible(False)
            self.listMenu_Feuilles_all_Albums.setVisible(False)
            self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
            self.listMenu_Feuilles_all_Dossiers.setVisible(False)

            self.listMenu_Fleur.setVisible(False)

            self.Information_label.setVisible(True)
        except:
            pass

        self.setFocus(self.listMenu_Initialisation_players)
        itemSelection = self.listMenu_Initialisation_players.getListItem(
                self.listMenu_Initialisation_players.getSelectedPosition()).getLabel()
        debug('item player selected is : ' + str(itemSelection), xbmc.LOGNOTICE)
        itemPosition = self.listMenu_Initialisation_players.getSelectedPosition()

        self.playerid = self.dictionnairedesplayers[itemPosition + 1]['playerid']
        debug('playerid : ' + str(self.playerid) , xbmc.LOGNOTICE)

        self.Players = outils.WhatAreThePlayers()

        # interesting which one below is correct ?
        self.Players.playerSelectionID = self.playerid
        #self.Players.setPlayerSelectionID(self.playerid)

        self.playername = self.dictionnairedesplayers[itemPosition + 1]['name']
        debug('playername : ' + str(self.playername), xbmc.LOGNOTICE)
        self.Players.playerSelectionName = self.playername

        self.initialisationDone()

    def initialisationDone(self):
        self.Information_label.setVisible(False)
        #self.listMenu_Initialisation_server.setVisible(False)
        self.listMenu_Initialisation_players.setVisible(False)
        self.listMenu_Initialisation_players.reset()
        self.listMenu_Racine.setVisible(True)
        self.setFocus(self.listMenu_Racine)


    def navigationFromMenuRacine(self):

        itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

        if itemSelectionRacine == translation(32040 , 'Now Playing'):
            # activer frame ecouteEnCours
            self.Abonnement.set() # need to renew subscribe after interup
            self.jivelette = framePlaying.SlimIsPlaying()

            self.WindowPlaying = xbmcgui.getCurrentWindowId()
            debug('fenetre en cours n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)

            # todo : test inversion show et doModal
            self.jivelette.show()
            time.sleep(0.5)
            self.update_now_is_playing()
            #self.jivelette.doModal()
            del self.jivelette

        elif itemSelectionRacine == translation(32041 , 'My Music'):

            if not self.music_branch_populated:
                self.listMenu_MyMusic.addItems(self.listeMyMusicPourMenuMyMusic)
            self.setFocus(self.listMenu_MyMusic)

        elif itemSelectionRacine == translation(32042 , 'I-Radio' ):
            self.listMenu_Branches.reset()
            self.listMenu_Branches.setVisible(True)
            self.setFocus(self.listMenu_Branches)

            new_radio = plugin.Plugin_Generique(parent=self)
            self.liste_du_menu_branche_des_plugins = new_radio.le_menu_branche('radios')
            self.setFocus(self.listMenu_Branches)


        elif itemSelectionRacine == translation(32043 , 'My Apps'):

            if self.can_myapps:
                self.listMenu_Branches.reset()
                self.listMenu_Branches.setVisible(True)
                self.setFocus(self.listMenu_Branches)

                new_apps = plugin.Plugin_Generique(parent=self)
                self.liste_du_menu_branche_des_plugins = new_apps.le_menu_branche('apps')
                self.setFocus(self.listMenu_Branches)

            else:
                outils.functionNotPossible()

        elif itemSelectionRacine == translation(32044 , 'Favorites'):
            if self.can_favorites:
                self.listMenu_Branches.reset()
                self.listMenu_Branches.setVisible(False)

                new_favorites = plugin.Plugin_Favorites(self)
                self.liste_du_menu_branche_des_plugins = new_favorites.le_menu_branche('favorites')
            else:
                outils.functionNotPossible()
                
        elif  itemSelectionRacine == translation(32045 , 'Extras'):
            debug('selection Extras' , xbmc.LOGNOTICE)
            self.listMenu_Extras.reset()
            self.listMenu_Extras.addItems(self.listeExtraPourMenuExtras)
            self.listMenu_Branches.setVisible(False)
            self.listMenu_Extras.setVisible(True)
            self.setFocus(self.listMenu_Extras)
            #self.navigationFromMenuBrancheExtras()

        elif itemSelectionRacine == translation(32046 , 'Quit'):
            debug('menu Quit requested in frameMenu', xbmc.LOGNOTICE)
            self.quit()

    def navigationFromMenusMyMusic(self):

        self.itemSelectionBranche = self.listMenu_MyMusic.getListItem(
                            self.listMenu_MyMusic.getSelectedPosition()).getLabel()
        self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
        debug('position curseur sur menu après connect : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)
        self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
        NumeroItemSelectionBranche = self.listMenu_MyMusic.getSelectedPosition()
        try:
                # root
                self.listMenu_Racine.setVisible(True)
                # branchs
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                # leaves
                self.listMenu_Feuilles.setVisible(False)
                # flower Todo : delete it ?
                self.listMenu_Fleur.setVisible(False)
        except:
                pass

        if self.itemSelectionBranche == translation(32050, 'Album Artists'):
            try:
                # root
                self.listMenu_Racine.setVisible(True)
                # branch
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                # leaves
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(True)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                # flower
                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_ArtistAlbums)
            self.listMenu_Feuilles_ArtistAlbums.controlLeft(self.listMenu_MyMusic)

            if not self.ArtistAlbums_populated:
                new_music_ArtistAlbums = plugin.MyMusic(self)
                new_music_ArtistAlbums.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche,
                                                       label_branche='Album Artists')

        elif self.itemSelectionBranche == translation(32051 , 'All Artists'):
            try:
                # root
                self.listMenu_Racine.setVisible(True)
                #branch
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                #leaves
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(True)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                #flower
                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Artists)
            self.listMenu_Feuilles_all_Artists.controlLeft(self.listMenu_MyMusic)

            if not self.all_Artists_populated:
                new_music = plugin.MyMusic(self)
                new_music.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche,
                                          label_branche='All Artists')
        
        elif self.itemSelectionBranche == translation(32053 , 'Albums'):
            try:
                self.listMenu_Racine.setVisible(True)
                
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(True)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Albums)
            self.listMenu_Feuilles_all_Albums.controlLeft(self.listMenu_MyMusic)

            if not self.all_albums_populated:
                new_music = plugin.MyMusic(self)
                new_music.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche,
                                          label_branche='Albums')

        elif self.itemSelectionBranche == translation(32058 , default='Random Mix'):

            try:
                self.listMenu_Racine.setVisible(True)
                
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(True)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            if self.can_randomplay:
                
                self.listMenu_Feuilles_RandomMix.reset()
    
                itemtampon = xbmcgui.ListItem()
                itemtampon.setLabel(translation(32080, 'Song mix' ))
                self.listMenu_Feuilles_RandomMix.addItem(itemtampon)
                itemtampon = xbmcgui.ListItem()
                itemtampon.setLabel(translation(32081 , 'Album mix' ))
                self.listMenu_Feuilles_RandomMix.addItem(itemtampon)
                itemtampon = xbmcgui.ListItem()
                itemtampon.setLabel(translation(32082 , 'Artist mix' ))
                self.listMenu_Feuilles_RandomMix.addItem(itemtampon)
                itemtampon = xbmcgui.ListItem()
                itemtampon.setLabel(translation(32083 , 'Years mix' ))
                self.listMenu_Feuilles_RandomMix.addItem(itemtampon)

                self.setFocus(self.listMenu_Feuilles_RandomMix)
    
                self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_RandomMix)
                self.listMenu_Feuilles_RandomMix.controlLeft(self.listMenu_MyMusic)
            else:
                # the server is not able  -> print not possible
                outils.functionNotPossible()


        elif self.itemSelectionBranche == translation(32059, 'Music Folder'):
            try:
                self.listMenu_Racine.setVisible(True)

                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)

                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(True)

                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Dossiers)
            self.listMenu_Feuilles_all_Dossiers.controlLeft(self.listMenu_MyMusic)

            if not self.all_dossiers_populated:
                new_music = plugin.MyMusic(self)
                new_music.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche,
                                          label_branche='Music folder')

        else:
            #todo :  write the other actions from the menu_music
            self.listMenu_Feuilles.reset()
            debug('FNYI : frameMenu.py navigationFromMenusMyMusic ', xbmc.LOGNOTICE)
            outils.functionNotYetImplemented()

    def navigationFromMenuBranche(self):

        self.itemSelectionBranche = self.listMenu_Branches.getListItem(
            self.listMenu_Branches.getSelectedPosition()).getLabel()

        NumeroItemSelectionBranche = self.listMenu_Branches.getSelectedPosition()

        # affichage en bas écran dans un label le menu en cours
        self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
        debug('position curseur sur menu Branche : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)

        self.listMenu_Racine.controlRight(self.listMenu_Branches)

        if self.itemSelectionRacine == translation(32041 , 'My Music'):
            # it must not be possible as we are in menu Branch and not in menu MyMusic
            pass

        if self.itemSelectionRacine == translation(32042 , 'I-Radio' ) or \
                self.itemSelectionRacine == translation(32043 , 'My Apps'):

            try:
                # self.listMenu_Branches.reset() # Todo à voir plus tard si on reset les lists menu
                self.listMenu_Racine.setVisible(True)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(True)
                self.listMenu_Extras.setVisible(False)

                self.listMenu_Feuilles.setVisible(True)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            new_feuille = plugin.Plugin_Generique(parent=self)

        # Todo : delete lines below because we cannot have branch='Favorites'4
        elif self.itemSelectionRacine == translation(32044 , 'Favorites'):
            new_feuille = plugin.Plugin_Favorites(self)

        new_feuille.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche)
    # fin fonction navigationFromMenuBranche

    def navigationFromMenuFeuilles(self):

        itemSelectionFeuille = self.listMenu_Feuilles.getListItem(
                    self.listMenu_Feuilles.getSelectedPosition()).getLabel()
        listitemSelection = self.listMenu_Feuilles.getSelectedItem()
        itemIdSelection = self.listMenu_Feuilles.getListItem(
            self.listMenu_Feuilles.getSelectedPosition()).getProperty('id')
        hasitems = self.listMenu_Feuilles.getListItem(
            self.listMenu_Feuilles.getSelectedPosition()).getProperty('hasitems')
        artist = self.listMenu_Feuilles.getListItem(
            self.listMenu_Feuilles.getSelectedPosition()).getProperty('artist')
        NumeroItemSelectionFeuille = self.listMenu_Feuilles.getSelectedPosition()

        debug('label dans menu Feuille : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        debug('id dans menu Feuille : ' + itemIdSelection, xbmc.LOGNOTICE)
        debug('artist dans menu Feuille : ' + artist , xbmc.LOGNOTICE)
        debug('hasitems dans menu Feuille : ' + hasitems, xbmc.LOGNOTICE)
        debug('numéro dans menu Feuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

        self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)

        # if hasitem == 1:
        # dig one  more time (no recursive)
        #if hasitems == '1':
            #self.les_menus_fleurs_Generic(NumeroItemSelectionFeuille)  # is it possible todo a recursive fonction ?

        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(False)
        self.listMenu_Branches.setVisible(True)
        self.listMenu_Extras.setVisible(False)

        self.listMenu_Feuilles.setVisible(True)

        self.listMenu_Fleur.setVisible(True)

        #self.setFocus(self.listMenu_Fleur)
        # todo : is it right this ?
        if self.itemSelectionRacine == translation(32041 , 'My Music'):
            itemSelection = self.listMenu_Feuilles.getListItem(
                self.listMenu_Feuilles.getSelectedPosition()).getProperty('artist_id')
            debug('id item artist : ' + str(itemSelection) , xbmc.LOGNOTICE)
            itemalternate = self.listMenu_Feuilles.getSelectedItem().getProperty('artist_id')
            debug('id item artist alternate : ' + str(itemalternate) , xbmc.LOGNOTICE)

            self.listMenu_MyMusic.setVisible(True)

            if itemSelection:
                new_menu = plugin.MyMusic(parent=self)
                new_menu.le_menu_fleurs(itemSelection)

        else:
            new_menu = plugin.Plugin_Generique(parent=self)
            new_menu.le_menu_fleurs(numeroItemSelectionFeuille=NumeroItemSelectionFeuille)

    def navigationFromMenuFeuilles_all_Artists(self):

        itemSelectionFeuille = self.listMenu_Feuilles_all_Artists.getListItem(
                    self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getLabel()
        listitemSelection = self.listMenu_Feuilles_all_Artists.getSelectedItem()
        itemIdSelection = self.listMenu_Feuilles_all_Artists.getListItem(
            self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('id')
        hasitems = self.listMenu_Feuilles_all_Artists.getListItem(
            self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('hasitems')
        artist = self.listMenu_Feuilles_all_Artists.getListItem(
            self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('artist')
        NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Artists.getSelectedPosition()

        debug('label dans menu Feuille All Artists : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        debug('id dans menu Feuille All Artists : ' + itemIdSelection, xbmc.LOGNOTICE)
        debug('artist dans menu Feuille All Artists : ' + artist , xbmc.LOGNOTICE)
        debug('hasitems dans menu Feuille All Artists : ' + hasitems, xbmc.LOGNOTICE)
        debug('numéro dans menu Feuille All Artists : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

        self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)

        # if hasitem == 1:
        # dig one  more time (no recursive)
        #if hasitems == '1':
            #self.les_menus_fleurs_Generic(NumeroItemSelectionFeuille)  # is it possible todo a recursive fonction ?

        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(True)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(False)

        self.listMenu_Feuilles.setVisible(False)
        self.listMenu_Feuilles_all_Artists.setVisible(True)
        self.listMenu_Feuilles_all_Albums.setVisible(False)
        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
        self.listMenu_Feuilles_RandomMix.setVisible(False)

        self.listMenu_Fleur.setVisible(False)
        #self.listMenu_Fleur.setVisible(True)
        self.setFocus(self.listMenu_Feuilles_all_Artists)

        itemSelection = self.listMenu_Feuilles_all_Artists.getListItem(
            self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('artist_id')
        debug('id item artist : ' + str(itemSelection) , xbmc.LOGNOTICE)
        itemalternate = self.listMenu_Feuilles_all_Artists.getSelectedItem().getProperty('artist_id')
        debug('id item artist alternate : ' + str(itemalternate) , xbmc.LOGNOTICE)

        new_menu = plugin.MyMusic(self)
        new_menu.le_menu_fleurs('All Artists' , itemSelection)
    
    def navigationFromMenuFeuilles_all_Albums(self):
        # todo write it

        itemSelectionFeuille = self.listMenu_Feuilles_all_Albums.getListItem(
            self.listMenu_Feuilles_all_Albums.getSelectedPosition()).getLabel()
        listitemSelection = self.listMenu_Feuilles_all_Albums.getSelectedItem()
        itemIdSelection = self.listMenu_Feuilles_all_Albums.getListItem(
            self.listMenu_Feuilles_all_Albums.getSelectedPosition()).getProperty('id')
        hasitems = self.listMenu_Feuilles_all_Albums.getListItem(
            self.listMenu_Feuilles_all_Albums.getSelectedPosition()).getProperty('hasitems')
        artist = self.listMenu_Feuilles_all_Albums.getListItem(
            self.listMenu_Feuilles_all_Albums.getSelectedPosition()).getProperty('artist')
        NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Albums.getSelectedPosition()

        debug('label dans menu Feuille All Albums : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        debug('id dans menu Feuille All Albums : ' + itemIdSelection, xbmc.LOGNOTICE)
        debug('artist dans menu Feuille All Albums : ' + artist, xbmc.LOGNOTICE)
        debug('hasitems dans menu Feuille All Albums : ' + hasitems, xbmc.LOGNOTICE)
        debug('numéro dans menu Feuille All Albums : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

        self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)

        # if hasitem == 1:
        # dig one  more time (no recursive)
        # if hasitems == '1':
        # self.les_menus_fleurs_Generic(NumeroItemSelectionFeuille)  # is it possible todo a recursive fonction ?

        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(True)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(False)

        self.listMenu_Feuilles.setVisible(False)
        self.listMenu_Feuilles_all_Artists.setVisible(False)
        self.listMenu_Feuilles_all_Albums.setVisible(True)
        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
        self.listMenu_Feuilles_RandomMix.setVisible(False)

        self.listMenu_Fleur.setVisible(False)

        self.setFocus(self.listMenu_Feuilles_all_Albums)

        itemSelection = self.listMenu_Feuilles_all_Albums.getListItem(
            self.listMenu_Feuilles_all_Albums.getSelectedPosition()).getProperty('album_id')
        debug('id item album : ' + str(itemSelection), xbmc.LOGNOTICE)
        itemalternate = self.listMenu_Feuilles_all_Albums.getSelectedItem().getProperty('album_id')
        debug('id item album alternate : ' + str(itemalternate), xbmc.LOGNOTICE)

        new_menu = plugin.MyMusic(self)
        new_menu.le_menu_fleurs('Albums', itemSelection)
    # fin navigationFromMenuFeuilles_all_Albums

    def navigationFromMenuFeuilles_ArtistAlbums(self):
        # todo write it

        itemSelectionFeuille = self.listMenu_Feuilles_ArtistAlbums.getListItem(
            self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getLabel()
        listitemSelection = self.listMenu_Feuilles_ArtistAlbums.getSelectedItem()
        itemIdSelection = self.listMenu_Feuilles_ArtistAlbums.getListItem(
            self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getProperty('id')

        artist = self.listMenu_Feuilles_ArtistAlbums.getListItem(
            self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getProperty('artist')
        NumeroItemSelectionFeuille = self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()

        debug('label dans menu Feuille ArtistAlbums : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        debug('id dans menu Feuille ArtistAlbums : ' + itemIdSelection, xbmc.LOGNOTICE)
        debug('artist dans menu Feuille ArtistAlbums : ' + artist, xbmc.LOGNOTICE)
        debug('numéro dans menu Feuille ArtistAlbums : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

        self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)

        # if hasitem == 1:
        # dig one  more time (no recursive)
        # if hasitems == '1':
        # self.les_menus_fleurs_Generic(NumeroItemSelectionFeuille)  # is it possible todo a recursive fonction ?

        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(True)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(False)

        self.listMenu_Feuilles.setVisible(False)
        self.listMenu_Feuilles_all_Artists.setVisible(False)
        self.listMenu_Feuilles_all_Albums.setVisible(False)
        self.listMenu_Feuilles_ArtistAlbums.setVisible(True)
        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
        self.listMenu_Feuilles_RandomMix.setVisible(False)

        self.listMenu_Fleur.setVisible(False)

        self.setFocus(self.listMenu_Feuilles_ArtistAlbums)

        itemSelection = self.listMenu_Feuilles_ArtistAlbums.getListItem(
            self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getProperty('album_id')
        debug('id item album : ' + str(itemSelection), xbmc.LOGNOTICE)
        itemalternate = self.listMenu_Feuilles_ArtistAlbums.getSelectedItem().getProperty('album_id')
        debug('id item album alternate : ' + str(itemalternate), xbmc.LOGNOTICE)

        new_menuArtistAlbum = plugin.MyMusic(self)
        new_menuArtistAlbum.le_menu_fleurs('ArtistAlbums', itemSelection)
    # fin navigationFromMenuFeuilles_ArtistAlbums

    def navigationFromMenuFeuilles_RandomMix(self):
        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(True)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(False)

        self.listMenu_Feuilles.setVisible(False)
        self.listMenu_Feuilles_all_Artists.setVisible(False)
        self.listMenu_Feuilles_all_Albums.setVisible(False)
        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
        self.listMenu_Feuilles_RandomMix.setVisible(True)
        self.listMenu_Feuilles_all_Dossiers.setVisible(False)

        self.listMenu_Fleur.setVisible(True)

        itemSelectionFeuille = self.listMenu_Feuilles_RandomMix.getListItem(
                    self.listMenu_Feuilles_RandomMix.getSelectedPosition()).getLabel()
        listitemSelection = self.listMenu_Feuilles_RandomMix.getSelectedItem()
        NumeroItemSelectionFeuille = self.listMenu_Feuilles_RandomMix.getSelectedPosition()

        self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)

        if itemSelectionFeuille ==  translation(32080 , 'Song mix' ) :
            requete = self.playerid + ' randomplay tracks'
            title = translation(32080 , 'Song mix' )

        elif itemSelectionFeuille == translation(32081 , 'Album mix' ):
            requete = self.playerid + ' randomplay albums'
            title = translation(32081 , 'Album mix')

        elif itemSelectionFeuille == translation(32082 , 'Artist mix' ):
            requete = self.playerid + ' randomplay contributors'
            title = translation(32082 , 'Artist mix' )

        elif itemSelectionFeuille == translation(32083 , 'Years mix' ):
            requete = self.playerid + ' randomplay year'
            title = translation(32083 , 'Years mix' )

        self.InterfaceCLI.viderLeBuffer()
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()

        self.Abonnement.set()
        self.frameRandomPlay = framePlaylist.PlaylistPlugin()

        self.frameRandomPlay.show()
        self.frameRandomPlay.listMenu_playlist.reset()
        self.update_random_mix_Playlist()

    def navigationFromMenuFeuilles_all_Dossiers(self):
        # todo write it

        itemSelectionFeuille = self.listMenu_Feuilles_all_Dossiers.getListItem(
            self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getLabel()
        listitemSelection = self.listMenu_Feuilles_all_Dossiers.getSelectedItem()
        itemIdSelection = self.listMenu_Feuilles_all_Dossiers.getListItem(
            self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getProperty('folder_id')
        filename = self.listMenu_Feuilles_all_Dossiers.getListItem(
            self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getProperty('filename')
        type = self.listMenu_Feuilles_all_Dossiers.getListItem(
            self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getProperty('type')
        NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()

        debug('label dans menu Feuille All Dossiers : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        debug('id dans menu Feuille All Dossiers : ' + itemIdSelection, xbmc.LOGNOTICE)
        debug('fichier dans menu Feuille All Dossiers : ' + filename, xbmc.LOGNOTICE)
        debug('type dans menu Feuille All Dossiers : ' + type , xbmc.LOGNOTICE)

        self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)

        # if hasitem == 1:
        # dig one  more time (no recursive)
        # if hasitems == '1':
        # self.les_menus_fleurs_Generic(NumeroItemSelectionFeuille)  # is it possible todo a recursive fonction ?

        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(True)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(False)

        self.listMenu_Feuilles.setVisible(False)
        self.listMenu_Feuilles_all_Artists.setVisible(False)
        self.listMenu_Feuilles_all_Albums.setVisible(False)
        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
        self.listMenu_Feuilles_all_Dossiers.setVisible(True)
        self.listMenu_Feuilles_RandomMix.setVisible(False)


        self.setFocus(self.listMenu_Feuilles_all_Dossiers)

        itemSelection = self.listMenu_Feuilles_all_Dossiers.getListItem(
            self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getProperty('folder_id')
        debug('id item folder : ' + str(itemSelection), xbmc.LOGNOTICE)
        itemalternate = self.listMenu_Feuilles_all_Dossiers.getSelectedItem().getProperty('folder_id')
        debug('id item folder alternate : ' + str(itemalternate), xbmc.LOGNOTICE)

        new_menu = plugin.MyMusic(self)
        new_menu.le_menu_fleurs('Dossiers', itemSelection)
    # fin navigationFromMenuFeuilles_all_Dossiers

    def navigationFromMenuBrancheExtras(self):

        debug(' entrée dans le_menus_branche_extras', xbmc.LOGNOTICE)

        self.listMenu_Racine.setVisible(True)

        self.listMenu_MyMusic.setVisible(False)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(True)

        self.listMenu_Feuilles_Extras.setVisible(True)
        self.listMenu_Feuilles_all_Artists.setVisible(False)
        self.listMenu_Feuilles_RandomMix.setVisible(False)
        self.listMenu_Fleur.setVisible(False)

        self.listMenu_Racine.controlRight(self.listMenu_Extras)
        self.listMenu_Extras.controlLeft(self.listMenu_Racine)
        self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)

        itemSelectionBranche = self.listMenu_Extras.getListItem(
                    self.listMenu_Extras.getSelectedPosition()).getLabel()
        NumeroItemSelectionBranche = self.listMenu_Extras.getSelectedPosition()
        if NumeroItemSelectionBranche == 0:
            #players
            self.listMenu_Feuilles_Extras.reset()
            self.populate_Menu_Players()
            #self.players_action()
        elif NumeroItemSelectionBranche == 1:
            self.listMenu_Feuilles_Extras.reset()
            outils.functionNotYetImplemented()

        elif NumeroItemSelectionBranche == 2:
            self.listMenu_Feuilles_Extras.reset()
            outils.functionNotYetImplemented()

    def navigationFromMenuFeuillesExtras(self):

        self.listMenu_Extras.setVisible(True)
        self.listMenu_Feuilles_Extras.setVisible(True)
        self.listMenu_Feuilles_Extras.controlLeft(self.listMenu_Extras)
        self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)
        self.listMenu_Extras.controlLeft(self.listMenu_Racine)

        NumeroItemSelectionBranche = self.listMenu_Extras.getSelectedPosition()
        if NumeroItemSelectionBranche == 0:
            # players
            NumeroItemSelectionFeuille = self.listMenu_Feuilles_Extras.getSelectedPosition()
            itemSelectionFeuille = self.listMenu_Feuilles_Extras.getListItem(
                    self.listMenu_Feuilles_Extras.getSelectedPosition()).getLabel()

            playerid = self.listMenu_Feuilles_Extras.getListItem(
                self.listMenu_Feuilles_Extras.getSelectedPosition()).getProperty('playerid')
            etat = self.listMenu_Feuilles_Extras.getListItem(
                self.listMenu_Feuilles_Extras.getSelectedPosition()).getProperty('power')

            self.InterfaceCLI.viderLeBuffer()

            if etat == '0':
                #<playerid> power <0|1|?|>
                requete = playerid + ' power 1'
                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()

            elif etat == '1':
                requete = playerid + ' power 0'
                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()

            else:
                pass            
            #todo : activate deactivate player won't work ? because dictionnaryplayer is not updated
            # l'état des players a changé , réinitialisation du dictionnaire des players

            self.Players = outils.WhatAreThePlayers()
            self.dictionnairedesplayers = dict()
            self.dictionnairedesplayers = self.Players.recherchedesPlayers(self.InterfaceCLI, self.recevoirEnAttente)
            # recherche d'un player actif et si actif vrai . actif = isplaying
            self.actif, index_dictionnairedesPlayers, self.playerid = self.Players.playerActif(
                self.dictionnairedesplayers)
            self.initialisationPlayeur()
            self.listMenu_Feuilles_Extras.reset()
            self.populate_Menu_Players()
            #self.navigationFromMenuInitialisation()

    def populate_Menu_Players(self):

        nombredePlayers = self.dictionnairedesplayers[0]['count']
        dictionnairedesplayerscopy = copy.deepcopy(self.dictionnairedesplayers[1:])
        for unplayer in dictionnairedesplayerscopy:
            menuunplayer = xbmcgui.ListItem()
            labeltemp = unplayer['name']
            menuunplayer.setProperty('power' , unplayer['power'])
            menuunplayer.setProperty('playerid' , unplayer['playerid'])
            if unplayer['power'] == '0':
                # player éteint on peut l'allumer
                labeltemp = labeltemp + ' : ' + translation(32800 , 'Turn on ' )
            elif unplayer['power'] == '1':
                labeltemp = labeltemp + ' : ' + translation(32801 , 'Turn off ')
            else:
                labeltemp = labeltemp + ' : ' + translation(32801, 'state unknow')

            menuunplayer.setLabel(labeltemp)
            #debug('populate player menu' + labeltemp + unplayer['playerid']  , xbmc.LOGNOTICE) # ! could be unicode
            self.listMenu_Feuilles_Extras.addItem(menuunplayer)


        self.listMenu_Feuilles_Extras.setVisible(True)
        del dictionnairedesplayerscopy

    def players_action(self):
        '''todo'''
        pass

    def list_Menu_Navigation(self):
        '''
        navigation through menus
        '''
        # rappel des valeurs pour positionnement

        # Update list_item label when navigating through the list.
        self.itemSelectionRacine = ''
        self.itemSelectionBranche = ''
        self.itemSelectionFeuille = ''
        self.itemSelectionFleur = ''

        self.itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

        # affichage en bas écran dans un label le menu en cours
        #self.list_racine_label.setLabel('# ' + self.itemSelectionRacine)
        debug( 'position curseur sur menu : ' + self.itemSelectionRacine, xbmc.LOGDEBUG)

        try:
            if self.getFocus() == self.listMenu_Initialisation_server:
                self.listMenu_Initialisation_server.setVisible(True)
                self.listMenu_Initialisation_players.setVisible(False)

                self.listMenu_Racine.setVisible(False)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)

                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                self.listMenu_Feuilles_Extras.setVisible(False)

                self.listMenu_Fleur.setVisible(False)

                self.itemSelectionInitialisation = self.listMenu_Initialisation_server.getListItem(
                    self.listMenu_Initialisation_server.getSelectedPosition()).getLabel()
                self.list_racine_label.setLabel('::' + self.itemSelectionInitialisation)
                debug('position curseur sur menu serveur : ' + self.itemSelectionInitialisation, xbmc.LOGNOTICE)

            elif self.getFocus() == self.listMenu_Initialisation_players:

                self.listMenu_Initialisation_server.setVisible(False)
                self.listMenu_Initialisation_players.setVisible(True)

                self.listMenu_Racine.setVisible(False)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)

                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_all_Albums.setVisible(False)
                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                self.listMenu_Feuilles_Extras.setVisible(False)

                self.listMenu_Fleur.setVisible(False)

                self.itemSelectionInitialisation = self.listMenu_Initialisation_players.getListItem(
                    self.listMenu_Initialisation_players.getSelectedPosition()).getLabel()
                self.list_racine_label.setLabel('::' + self.itemSelectionInitialisation)
                debug('position curseur sur menu players : ' + self.itemSelectionInitialisation, xbmc.LOGNOTICE)

            elif self.getFocus() == self.listMenu_Racine:

                # on récupère le label de l'item du menu principal sur lequel on est positionné
                self.itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

                # affichage en bas écran dans un label le menu en cours
                self.list_racine_label.setLabel('::' + self.itemSelectionRacine)
                debug( 'position curseur sur menu : ' + self.itemSelectionRacine, xbmc.LOGNOTICE)
                # remise à blanc des sous labels
                self.list_item_branche_label.setLabel('')
                self.list_item_feuille_label.setLabel('')

                if self.itemSelectionRacine == translation(32041 , 'My Music'): # condition always true. never mind
                                                           # we will delete them later after try et rewriting the code

                    self.listMenu_Initialisation_server.setVisible(False)
                    self.listMenu_Initialisation_players.setVisible(False)

                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(True)
                    self.listMenu_Branches.setVisible(False)
                    self.listMenu_Extras.setVisible(False)

                    self.listMenu_Feuilles.setVisible(False)
                    self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                    self.listMenu_Feuilles_all_Artists.setVisible(False)
                    self.listMenu_Feuilles_all_Albums.setVisible(False)
                    self.listMenu_Feuilles_RandomMix.setVisible(False)
                    self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                    self.listMenu_Feuilles_Extras.setVisible(False)

                    self.listMenu_Fleur.setVisible(False)

                    try:
                        self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                        self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                    except:
                        pass

                    if self.getFocus() == self.listMenu_MyMusic:

                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(True)
                        self.listMenu_Branches.setVisible(False)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)

                        # on récupère le label de l'item sur lequel on est positionné
                        itemSelectionBranche = self.listMenu_MyMusic.getListItem(
                            self.listMenu_MyMusic.getSelectedPosition()).getLabel()
                        debug('position dans menu My Music : ' + itemSelectionBranche, xbmc.LOGDEBUG)
                        self.list_item_feuille_label.setLabel('')

                        # affichage en bas écran dans un label le menu en cours
                        self.list_item_branche_label.setLabel(' :: ' + itemSelectionBranche)

                        NumeroItemSelectionBranche = self.listMenu_MyMusic.getSelectedPosition()

                        self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                        self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                        # à xompléter en descendant dans les menus

                        if self.getFocus() == self.listMenu_Feuilles_ArtistAlbums:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(True)
                                self.listMenu_Branches.setVisible(False)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(True)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles_ArtistAlbums.getListItem(
                                self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille ArtistAlbums : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')
                            NumeroItemSelectionFeuille = self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()
                            hasitems = self.listMenu_Feuilles_ArtistAlbums.getListItem(
                                self.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getProperty('hasitems')

                            debug('flowers get an hasitem : ' + str(hasitems), xbmc.LOGNOTICE)
                            # if hasitem == 1:
                            # dig one  more time (no recursive)
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                            self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_ArtistAlbums)
                            self.listMenu_Feuilles_ArtistAlbums.controlLeft(self.listMenu_MyMusic)


                        elif self.getFocus() == self.listMenu_Feuilles_all_Artists:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(True)
                                self.listMenu_Branches.setVisible(False)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_all_Artists.setVisible(True)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles_all_Artists.getListItem(
                                self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille All Artists : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')
                            NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Artists.getSelectedPosition()
                            hasitems = self.listMenu_Feuilles_all_Artists.getListItem(
                                self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('hasitems')

                            debug('flowers get an hasitem : ' + str(hasitems), xbmc.LOGNOTICE)
                            # if hasitem == 1:
                            # dig one  more time (no recursive)
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                            self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Artists)
                            self.listMenu_Feuilles_all_Artists.controlLeft(self.listMenu_MyMusic)

                        # fin if all artits

                        elif self.getFocus() == self.listMenu_Feuilles_all_Albums:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(True)
                                self.listMenu_Branches.setVisible(False)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(True)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles_all_Albums.getListItem(
                                self.listMenu_Feuilles_all_Albums.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille Album mix : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')

                            NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Albums.getSelectedPosition()
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                            self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                            self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Albums)
                            self.listMenu_Feuilles_all_Albums.controlLeft(self.listMenu_MyMusic)

                        elif self.getFocus() == self.listMenu_Feuilles_RandomMix:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(True)
                                self.listMenu_Branches.setVisible(False)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(True)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles_RandomMix.getListItem(
                                self.listMenu_Feuilles_RandomMix.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille Random mix : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')

                            NumeroItemSelectionFeuille = self.listMenu_Feuilles_RandomMix.getSelectedPosition()
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                            self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                            self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_RandomMix)
                            self.listMenu_Feuilles_RandomMix.controlLeft(self.listMenu_MyMusic)



                        elif self.getFocus() == self.listMenu_Feuilles_all_Dossiers:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(True)
                                self.listMenu_Branches.setVisible(False)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(True)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles_all_Dossiers.getListItem(
                                self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille Random mix : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')

                            NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Dossiers.getSelectedPosition()
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                            self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                            self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Dossiers)
                            self.listMenu_Feuilles_all_Dossiers.controlLeft(self.listMenu_MyMusic)



                elif self.itemSelectionRacine == translation(32042 , 'I-Radio' ):

                    try:
                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)
                    except:
                        pass
                    try:
                        self.listMenu_Racine.controlRight(self.listMenu_Branches)
                        self.listMenu_Branches.controlLeft(self.listMenu_Racine)
                        self.listMenu_Branches.controlRight(self.listMenu_Feuilles)
                        self.listMenu_Feuilles.controlLeft(self.listMenu_Branches)
                    except:
                        pass

                    if self.getFocus() == self.listMenu_Branches:

                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)

                        self.itemSelectionBranche = self.listMenu_Branches.getListItem(
                            self.listMenu_Branches.getSelectedPosition()).getLabel()

                        # affichage en bas écran dans un label le menu en cours
                        self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
                        debug('position curseur sur menu : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)
                        # remise à blanc des sous-labels
                        self.list_item_feuille_label.setLabel('')

                        self.listMenu_Racine.controlRight(self.listMenu_Branches)

                        if self.getFocus() == self.listMenu_Feuilles:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(False)
                                self.listMenu_Branches.setVisible(True)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(True)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles.getListItem(
                                self.listMenu_Feuilles.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')
                            NumeroItemSelectionFeuille = self.listMenu_Feuilles.getSelectedPosition()
                            hasitems = self.listMenu_Feuilles.getListItem(
                                self.listMenu_Feuilles.getSelectedPosition()).getProperty('hasitems')

                            debug('flowers get an hasitem : ' + str(hasitems), xbmc.LOGNOTICE)
                            # if hasitem == 1:
                            # dig one  more time (no recursive)
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                elif self.itemSelectionRacine == translation(32043 , 'My Apps'):

                    try:
                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)

                    except:
                        pass
                    try:
                        self.listMenu_Racine.controlRight(self.listMenu_Branches)
                        self.listMenu_Branches.controlLeft(self.listMenu_Racine)
                        self.listMenu_Branches.controlRight(self.listMenu_Feuilles)
                        self.listMenu_Feuilles.controlLeft(self.listMenu_Branches)
                    except:
                        pass

                    if self.getFocus() == self.listMenu_Branches:

                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)

                        self.itemSelectionBranche = self.listMenu_Branches.getListItem(
                            self.listMenu_Branches.getSelectedPosition()).getLabel()

                        # affichage en bas écran dans un label le menu en cours
                        self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
                        debug('position curseur sur menu : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)
                        # remise à blanc des sous-labels
                        self.list_item_feuille_label.setLabel('')

                        self.listMenu_Racine.controlRight(self.listMenu_Branches)

                        if self.getFocus() == self.listMenu_Feuilles:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(False)
                                self.listMenu_Branches.setVisible(True)
                                self.listMenu_Extras.setVisible(False)

                                self.listMenu_Feuilles.setVisible(True)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(False)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles.getListItem(
                                self.listMenu_Feuilles.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')
                            NumeroItemSelectionFeuille = self.listMenu_Feuilles.getSelectedPosition()
                            hasitems = self.listMenu_Feuilles.getListItem(
                                self.listMenu_Feuilles.getSelectedPosition()).getProperty('hasitems')

                            debug('flowers get an hasitem : ' + str(hasitems), xbmc.LOGNOTICE)
                            # if hasitem == 1:
                            # dig one  more time (no recursive)
                            debug('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)



                elif self.itemSelectionRacine == translation(32044 , 'Favorites'):
                    # favorites has a special frame rather a sub-menu ; it's a try
                    try:
                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(False)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)
                    except:
                        pass

                elif self.itemSelectionRacine == translation(32045 , 'Extras'):

                    try:
                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(False)
                        self.listMenu_Extras.setVisible(True)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)
                    except:
                        pass

                    if self.getFocus() == self.listMenu_Extras:

                        self.listMenu_Initialisation_server.setVisible(False)
                        self.listMenu_Initialisation_players.setVisible(False)

                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(False)
                        self.listMenu_Extras.setVisible(True)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_all_Albums.setVisible(False)
                        self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(True)

                        self.listMenu_Fleur.setVisible(False)

                        self.listMenu_Racine.controlRight(self.listMenu_Extras)
                        self.listMenu_Extras.controlLeft(self.listMenu_Racine)
                        self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)

                        itemSelectionBranche = self.listMenu_Extras.getListItem(
                            self.listMenu_Extras.getSelectedPosition()).getLabel()
                        # affichage en bas écran dans un label le menu en cours
                        self.list_item_branche_label.setLabel(' :: ' + itemSelectionBranche)
                        debug('position dans menu Extras : ' + str(itemSelectionBranche), xbmc.LOGNOTICE)
                        # remise à blanc
                        self.list_item_feuille_label.setLabel('')

                        NumeroItemSelectionBranche = self.listMenu_Branches.getSelectedPosition()

                        if self.getFocus() == self.listMenu_Feuilles_Extras:

                            try:
                                self.listMenu_Initialisation_server.setVisible(False)
                                self.listMenu_Initialisation_players.setVisible(False)

                                self.listMenu_Racine.setVisible(True)

                                self.listMenu_MyMusic.setVisible(False)
                                self.listMenu_Branches.setVisible(False)
                                self.listMenu_Extras.setVisible(True)

                                self.listMenu_Feuilles.setVisible(False)
                                self.listMenu_Feuilles_all_Artists.setVisible(False)
                                self.listMenu_Feuilles_all_Albums.setVisible(False)
                                self.listMenu_Feuilles_ArtistAlbums.setVisible(False)
                                self.listMenu_Feuilles_RandomMix.setVisible(False)
                                self.listMenu_Feuilles_all_Dossiers.setVisible(False)
                                self.listMenu_Feuilles_Extras.setVisible(True)

                                self.listMenu_Fleur.setVisible(False)
                            except:
                                pass

                            itemSelectionFeuille = self.listMenu_Feuilles_Extras.getListItem(
                                self.listMenu_Feuilles_Extras.getSelectedPosition()).getLabel()
                            debug('label dans menu Feuille des Extras : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                            self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                            # remise à blanc sous-label
                            self.list_item_fleur_label.setLabel('')

                            NumeroItemSelectionFeuille = self.listMenu_Feuilles_Extras.getSelectedPosition()
                            debug('NumeroItemSelectionFeuilleExtra : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                            self.listMenu_Racine.controlRight(self.listMenu_Extras)
                            self.listMenu_Extras.controlLeft(self.listMenu_Racine)
                            self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)
                            self.listMenu_Feuilles_Extras.controlLeft(self.listMenu_Extras)


                elif self.itemSelectionRacine == translation(32046 , 'Quit'):
                    pass

        except  (RuntimeError, SystemError): # take from original pyxbmct demo code
            pass

    # fin fonction list_Menu_Navigation

    def welcome(self):
        self.Information_label.setLabel( translation(32931, 'Welcome to this Squeeze Box Display'))

    def initialisationServeur(self):

        outils.recherchonsleServeur(self)
        # maintenant nous connaissons le serveur
        # on lance le thread de connexion permanente avec le serveur :
        self.InterfaceCLI = InterfaceCLIduLMS(self.rechercheduserveur.LMSCLIip,
                                              self.recevoirEnAttente,
                                              self.envoiEnAttente,
                                              self.demandedeStop)
        self.InterfaceCLI.start()
        while not self.InterfaceCLI.startDone:
            time.sleep(0.1)
        debug('Connexion vue dans fonction frameMenu  : ' + str(self.InterfaceCLI.connexionAuServeurReussie), xbmc.LOGNOTICE)
        if self.InterfaceCLI.connexionAuServeurReussie:
            debug('Resultat Connexion  : Bon ' , xbmc.LOGNOTICE)
        else:
            debug('Resultat Connexion  : Mauvais ' , xbmc.LOGNOTICE)
        if not self.InterfaceCLI.connexionAuServeurReussie:
            # erreur sur la connexion
            debug('Erreur Connexion echouée : '+ str(self.InterfaceCLI.connexionAuServeurReussie), xbmc.LOGNOTICE)
            self.Information_label.setLabel('Error Connection Echec - Cannot Continue ')
            #self.close()
            exit(30) # raise error
        debug('type InterfaceCLI -> ' + str(type(self.InterfaceCLI)) , xbmc.LOGDEBUG)

        while not self.InterfaceCLI.EtatDuThread:  # on attend que le thread soit bien démarré j'aurais pu utiliser un event ?
            time.sleep(0.1)

        #sorti de la boucle  ok ici c'est bon le thread de connexion a démarré excepté si la connexion n'est pas bonne

        debug('thread alive -> ' + str(self.InterfaceCLI.is_alive) + ' . type -> ' + str(type(self.InterfaceCLI.is_alive)) , xbmc.LOGDEBUG)

        if not self.InterfaceCLI.is_alive:
            # we cannot be here because the loop above should not break
            debug('thread is not alive -> error 33 ' , xbmc.LOGDEBUG)
            exit(33)
        # here the communication with server througth the self.InterfaceCLI started
        # each call with the server would be self.InterfaceCLI.méthode()
        # exemple : self.InterfaceCLI.sendtoCLISomething('can myapps items ?')
    # fin fonction initialisation serveur

    def initialisationPlayeur(self):
        '''Todo : merge with selectPlayer()

        '''

        self.Information_label.setLabel(translation(32930, 'Select One player in the list below'))
        self.listMenu_Initialisation_players.setVisible(True)
        self.Players = outils.WhatAreThePlayers()
        self.dictionnairedesplayers = dict()
        self.dictionnairedesplayers = self.Players.recherchedesPlayers(self.InterfaceCLI, self.recevoirEnAttente)
        # recherche d'un player actif et si actif vrai . actif = isplaying
        # fill the menu Select a player

        self.actif , index_dictionnairedesPlayers ,  self.playerid = self.Players.playerActif(self.dictionnairedesplayers)

        # todo test below
        #assert isinstance(index_dictionnairedesPlayers, object)
        #self.lePlayerActif = playerid[index_dictionnairedesPlayers]

        debug(str(self.actif) + '  ' + self.playerid, xbmc.LOGDEBUG)

        if self.actif:
            nombredeplayers = self.dictionnairedesplayers[0]['count']
            for x in range(1, nombredeplayers + 1):
                #if (self.dictionnairedesplayers[x]['connected'] == '1'):
                self.listMenu_Initialisation_players.addItem(self.dictionnairedesplayers[x]['name'])
            # todo : afficher dans une boite-liste les players et en évidence le player actif
            # or choose the player by user
            #
        else:
            line1 = " no player to listen to music , Exit program " + '\n' + \
                    " Error n° 36. Quit the programm , bye bye"
            xbmcgui.Dialog().ok('Players Problem', line1)
            self.quit()
            exit(36)
        self.setFocus(self.listMenu_Initialisation_players)
    # fin function initialisation players

    def testCapaciteServeur(self):

        self.InterfaceCLI.sendtoCLISomething('can musicfolder ?')
        recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
        if recupropre.find(('can|musicfolder')):
            if '1' in recupropre:
                self.can_musicfolder = True
            else:
                self.can_musicfolder = False
        else:
            self.can_musicfolder = False

        self.InterfaceCLI.sendtoCLISomething('can favorites items ?')
        recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
        if recupropre.startswith('can|favorites|items'):
            if '1' in recupropre:
                self.can_favorites = True
            else:
                self.can_favorites = False
        else:
            self.can_favorites = False

        self.InterfaceCLI.sendtoCLISomething('can myapps items ?')
        recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
        if recupropre.startswith('can|myapps|items'):
            if recupropre.endswith('1'):
                self.can_myapps = True
            else:
                self.can_myapps = False
        else:
            self.can_myapps = False

        self.InterfaceCLI.sendtoCLISomething('can randomplay ?')
        recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
        if recupropre.startswith('can|randomplay'):
            if recupropre.endswith('1'):
                self.can_randomplay = True
            else:
                self.can_randomplay = False
        else:
            self.can_randomplay = False

        # end fonction testCapaciteServeur()

    def set_artwork_size(self):
        self.InterfaceCLI.sendtoCLISomething('artworkspec add ' + str(self.sizecover_x) + 'x' + \
                                             str(self.sizecover_x) + '_p ' + self.playerid)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        if reponse.startswith('artwork'):
            # ok
            pass
        else:
            line1 = 'problème dans la synchronisation'
            xbmcgui.Dialog().ok('Bad synchronization', line1)

        debug("soumission ArtWork : " + reponse, xbmc.LOGNOTICE)
        # find fonction set_artwork_size

    def update_now_is_playing(self):
        '''This is the main loop when prompt the Frame now is playing
            and the frame use show()
            Todo : can replace by the same method inside the class frameNowisPlaying
            when the frame use doModal()
        '''
        self.Window_is_playing = xbmcgui.getCurrentWindowId()
        #debug('fenetre de player en maj n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        #debug('nouvelle fenetre de player n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        # activation de la souscription au serveur process = Thread(target=crawl, args=[urls[ii], result, ii])
        self.subscribe = Souscription(self.InterfaceCLI , self.playerid )
        self.subscribe.subscription()
        # todo Q : comment faire la gestion de l'arret de la boucle de souscription ?
        #      A : fonction resiliersouscription()

        while self.Abonnement.is_set():  # remember Abonnement is an thread event for souscription
            time.sleep(0.5)

            timeoutdeTestdelaBoucle = time.time() + 60 * 2  # 2 minutes from now -for testing
            timeoutdeRecherchedesPlayers = time.time() + 60 * 20  #todo toutes les 20 minutes nous rechercherons les players
            timeEntreeDansLaBoucle = time.time()
            compteur = 1
            titreenlecture = ''
            self.breakBoucle_A = False
            while (self.breakBoucle_A == False):  # Boucle A principale de Subscribe

                if time.time() > timeoutdeTestdelaBoucle:
                    debug('Timeout : break A  ', xbmc.LOGNOTICE)
                    self.jivelette.bouton_pause.setVisible(False)
                    self.jivelette.bouton_play.setVisible(False)
                    break

                if not self.Abonnement.is_set:
                    break

                if xbmc.Monitor().waitForAbort(0.5):
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
                #debug('trame recue suite à suscribe : ' + str(pourLog), xbmc.LOGDEBUG)
                ('\n'
                 '  exemple RadioParadise :\n'
                 '  b8:27:eb:cf:f2:c0 status - 2 subscribe:30 rescan:1 player_name:piCorePlayer player_connected:1 \n'
                 '  player_ip:192.168.1.15:35182 power:1 signalstrength:0 mode:play remote:1 \n'
                 '  -----------------------------------------------------------------------------------------------------  '
                 '  current_title:Echo & the Bunnymen  -  The Killing Moon time:1511.89265412712 rate:1 \n'
                 '  sync_master:b8:27:eb:cf:f2:c0 sync_slaves:00:04:20:17:1c:44 mixer volume:42 playlist repeat:0 \n'
                 '  playlist shuffle:0 playlist mode:off seq_no:0 playlist_cur_index:0 playlist_timestamp:1573925050.19126 \n'
                 '  playlist_tracks:1 digital_volume_control:1 remoteMeta:HASH(0x8bf3bd8) playlist index:0 id:-93629680 \n'
                 '  title: The Killing Moon\n'
                 '\n'
                 '                        ')
                '''
                exemple musique random :               
                b8:27:eb:cf:f2:c0 status - 2 subscribe:30 player_name:piCorePlayer player_connected:1 
                player_ip:192.168.1.15:55850 power:1 signalstrength:0 mode:play 
                ---------------------------------------------------------------------------------------------
                time:100.483604986191 rate:1 duration:314.826 can_seek:1 sync_master:b8:27:eb:cf:f2:c0 
                sync_slaves:00:04:20:17:1c:44 mixer volume:36 playlist repeat:0 playlist shuffle:0 playlist mode:off 
                seq_no:0 playlist_cur_index:10 playlist_timestamp:1573565762.11147 playlist_tracks:21 
                digital_volume_control:1 playlist index:10 id:23149 title:Boogie On Reggae Woman 
                playlist index:11 id:26702 title:Tears Dry On Their Own'
                '''
                #exemple playlist:
                # 00:04:20:17:1
                # c:44 | status | 0 | 200 | subscribe:10 | player_name:Squeezebox
                # Receiver | player_connected:1 | player_ip:192.168.1.17:31420 |
                # power:1 | signalstrength:92 | mode:play | time:31.1482262744904 | rate:1 | duration:238.893 | can_seek:1 | mixer
                # volume:100 | playlist repeat:0 | playlist shuffle:0 | playlist mode:off | seq_no:0 |
                # playlist_cur_index:4 | playlist_timestamp:1578669235.11137 | playlist_tracks:15 |
                # digital_volume_control:1 |
                # playlist index:0 | id:13304 | title:Foxy Lady |
                # playlist index:1 | id:11673 | title:Won't Get Fooled Again (ISOLATED DRUMS)|
                # playlist index:2|id:19938|title:Piste 2|
                # playlist index:3|id:16874|title:China Girl|
                # [...]
                # playlist index:14|id:21643|title:A Kind Of Magic

                # Todo : analyse du bloc, Done

                recupropre = self.InterfaceCLI.receptionReponseEtDecodage()

                if 'subscribe:-' in recupropre: # fin souscription the resiliersouscription is send by framePlaying or
                                                # else diplaying
                                                # the framePlaying  exits - function quit()
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
                    break

                if recupropre.startswith('quit'):
                     debug('recu commande quit in update_now_is_playing in frameMenu')
                     self.breakBoucle_A = True
                     self.Abonnement.clear()
                     break


                listeB = recupropre.split('subscribe:' + TIME_OF_LOOP_SUBSCRIBE +'|')
                # on élimine le début de la trame # attention doit correpondre à
                # la même valeur de subscribe dans ecoute.py
                try:
                    textC = listeB[1]  # on conserve la deuximème trame après suscribe...
                except IndexError:
                    continue
                    #pass
                listeRetour = textC.split('|')  # on obtient une liste des items
                dico = dict()  # pour chaque élement de la liste sous la forme <val1>:<val2>
                dico2 = {}
                for x in listeRetour:  # on la place dans un dictionnaire
                    c = x.split(':')  # sous la forme  key: value et <val1> devient la key
                    if dico.has_key(c[0]):  # nous avons déjà une occurence
                        pass
                    else:
                        clef = c[0]
                        dico[clef] = c[1]  # ensuite on pourra piocher dans le dico la valeur

                # debug(str(dico.viewitems()), xbmc.LOGDEBUG)
                '''
                exemple du dictionnaire radio  suite :
                dict_items([('mixer volume', '42'), ('playlist repeat', '0'), ('digital_volume_control', '1'), 
                ('rescan', '1'), ('player_ip', '192.168.1.15'), ('rate', '1'), ('sync_slaves', '00'), ('id', '-93629680'), 
                ('signalstrength', '0'), ('player_name', 'piCorePlayer'), 
                ('current_title', 'Echo & the Bunnymen  -  The Killing Moon'), ('title', ' The Killing Moon\r\n'), 
                ('playlist mode', 'off'), ('playlist_cur_index', '0'), ('playlist_timestamp', '1573925050.19126'), 
                ('playlist index', '0'), ('power', '1'), ('playlist_tracks', '1'), ('playlist shuffle', '0'), 
                ('sync_master', 'b8'), ('player_connected', '1'), ('remoteMeta', 'HASH(0x8bf3bd8)'), ('remote', '1'), 
                ('seq_no', '0'), ('mode', 'play'), ('time', '1511.89265412712')])
                '''

                try:
                    pourcentagedureejouee = 100 * float(dico['time']) / float(dico['duration'])
                    debug('percent duree : ' + str(pourcentagedureejouee) + ' - time: ' + dico['time'], xbmc.LOGDEBUG)
                except KeyError:
                    pourcentagedureejouee = 0

                try:
                    self.jivelette.slider_duration.setPercent(pourcentagedureejouee)
                except KeyError:
                    pass

                try:
                    self.jivelette.labelduree_jouee.setLabel(label= outils.getInHMS(dico['time']))
                except KeyError:
                    pass

                try:
                    self.jivelette.labelduree_fin.setLabel(label= outils.getInHMS(dico['duration']))
                except KeyError:
                    self.jivelette.labelduree_fin.setLabel(label= outils.getInHMS(0.0))

                # Todo : if it is a playlist it is not the same struct
                # so 'title' , 'time' and so on doesn't exist

                try:
                    nouveautitre = dico['title']
                except KeyError:
                    nouveautitre = ''
                    pass

                if not nouveautitre == titreenlecture:

                    try:
                        self.jivelette.labeltitre_1.reset()
                        self.jivelette.labeltitre_1.addLabel(label='[B]' + dico['current_title'] + '[/B]')
                    except KeyError:
                        self.jivelette.labeltitre_1.addLabel(label='')
                        pass

                    try:
                        titreenlecture = dico['title']
                        self.jivelette.labeltitre_2.reset()
                        self.jivelette.labeltitre_2.addLabel(label='[B]' + titreenlecture + '[/B]')
                    except KeyError:
                        self.jivelette.labeltitre_2.addLabel(label='')

                    self.InterfaceCLI.viderLeBuffer()
                    self.InterfaceCLI.sendtoCLISomething('album ?')
                    reponse  = self.InterfaceCLI.receptionReponseEtDecodage()
                    album = reponse.split('album|').pop()
                    self.jivelette.labelAlbum.reset()
                    if not '|album' in album:
                        self.jivelette.labelAlbum.addLabel(label='[B]' + album + '[/B]')

                    self.InterfaceCLI.viderLeBuffer()
                    self.InterfaceCLI.sendtoCLISomething('artist ?')
                    reponse  = self.InterfaceCLI.receptionReponseEtDecodage()
                    artist = reponse.split('artist|').pop()
                    self.jivelette.labelArtist.reset()
                    if not '|artist' in artist:
                        self.jivelette.labelArtist.addLabel(label='[B]' + artist + '[/B]')

                self.jivelette.update_coverbox(self.lmsip, self.lmswebport, self.playerid, compteur)

               # log pour voir
                compteur += 1
                timedutour = time.time()
                tempsparcouru = timedutour - timeEntreeDansLaBoucle
                debug(str(compteur) + ' tour de boucle : ' + str(tempsparcouru), xbmc.LOGDEBUG)
                debug('bool jivelette.threadRunning : ' + str(self.jivelette.threadRunning), xbmc.LOGNOTICE)
                if not self.jivelette.threadRunning:
                    debug(' jivelette.threadRunning is not True ', xbmc.LOGNOTICE)
                    #self.subscribe.resiliersouscription() # double emploi
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
                # effacer les boutons :
                # fin de la boucle A : sortie de subscribe
        # fin boucle while
        debug('End of Boucle of Squeeze in frameMenu , Bye', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        debug('Send resiliersouscription in A update now_is_playing() in frameMenu', xbmc.LOGNOTICE)
        self.InterfaceCLI.viderLeBuffer()
        debug('End of fonction update_now_is_playing in frameMenu , Bye', xbmc.LOGNOTICE)
    #fin fonction update_now_is_playing

    def stop_now_is_playing(self):
        pass

    def update_random_mix_Playlist(self):
        '''this is the main loop when prompt the Frame Random playlist'''

        debug(' entrée dans le random mix de la framePlaylist', xbmc.LOGNOTICE)
        self.Window_is_playing = xbmcgui.getCurrentWindowId()
        #debug('fenetre de player en maj n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        #debug('nouvelle fenetre de player n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        # activation de la souscription au serveur process = Thread(target=crawl, args=[urls[ii], result, ii])
        self.subscribe = Souscription(self.InterfaceCLI , self.playerid )
        self.subscribe.subscriptionLongue()
        compteur = 0
        self.frameRandomPlay.update_coverbox(lmsip=self.lmsip, lmswebport=self.lmswebport, playerid=self.playerid,
                                             compteur=compteur)
        old_current_index_title = ''
        Titre_of_index_0 = "absolutely_Nothing_Here,I_guess_this_title_does_not_really_exists"
        flagResetListe = False
        while self.Abonnement.is_set():
            if xbmc.Monitor().waitForAbort(0.5):
                self.Abonnement.clear()

            compteur = compteur + 1
            self.frameRandomPlay.update_coverbox(lmsip=self.lmsip, lmswebport=self.lmswebport,
                                                 playerid=self.playerid, compteur=compteur)

            reponse = self.InterfaceCLI.receptionReponseEtDecodage()

            if 'subscribe:-' in reponse:  # fin souscription the resiliersouscription is send by framePlaying or
                # else diplaying
                # the framePlaying  exits - function quit()
                #self.breakBoucle_A = True  # must exit the loop A but doesn't exist here
                self.Abonnement.clear()  # must exit the main loop
                break


            try:
                entete , atraiter = reponse.split('subscribe:' +  TIME_OF_LOOP_SUBSCRIBE + '|')

                '''
                exemple :
                00:04:20:17:1c:44|status|0|100|subscribe:10|player_name:Squeezebox Receiver|player_connected:1|
                player_ip:192.168.1.17:31021|power:1|signalstrength:96|mode:play|time:150.337900035858|rate:1|
                duration:888.555|can_seek:1|mixer volume:81|playlist repeat:0|playlist shuffle:0|playlist mode:off|
                seq_no:0|
                playlist_cur_index:2|
                playlist_timestamp:1577823454.11438|playlist_tracks:13|
                digital_volume_control:1|
                playlist index:0|id:9663|title:Chesky / Atmosphere|
                playlist index:1|id:7843|title:Fly Away|
                playlist index:2|id:10850|title:Track 2|
                playlist index:3|id:14972|title:Skin O' My Teeth|
                playlist index:4|id:27085|title:With My Own Two Hands (Feat. Ben Harper)|
                playlist index:5|id:8648|title:Sonata No.7 in D major, op.10 no.3 - IV. Rondo. Allegro|
                playlist index:6|id:14743|title:Breadfan|
                playlist index:7|id:7426|title:Idylle anglo-normande|
                playlist index:8|id:9861|title:Wolfgang Amadeus Mozart - Krânungsmesse (K. 317) - Agnus Dei|
                playlist index:9|id:27812|title:My Baby Wants to Rock & Roll|
                playlist index:10|id:19598|title:Santiano|
                playlist index:11|id:8286|title:Chill Out (Things Gonna Change)|
                playlist index:12|id:6011|title:A toutes les filles
                '''

                indexdecurrentTitle = atraiter.find('cur_index:')
                indexFincurrentTitle = atraiter.find('|', indexdecurrentTitle)
                playlist_current_index_title = atraiter[indexdecurrentTitle + 10: indexFincurrentTitle]
                debug('current_index_title :' + playlist_current_index_title, xbmc.LOGNOTICE)
                listedechamps = atraiter.split('|playlist index:')
                # traiter d'abord les temps :
                listeRetour = listedechamps[0].split('|')  # on obtient une liste des items
                dico = dict()  # pour chaque élement de la liste sous la forme <val1>:<val2>
                for x in listeRetour:  # on la place dans un dictionnaire
                    c = x.split(':')  # sous la forme  key: value et <val1> devient la key
                    clef = c[0]
                    dico[clef] = c[1]  # ensuite on pourra piocher dans le dico la valeur

                try:
                    pourcentagedureejouee = 100 * float(dico['time']) / float(dico['duration'])
                    debug('percent duree : ' + str(pourcentagedureejouee) + ' - time: ' + dico['time'],
                             xbmc.LOGNOTICE)
                except KeyError:
                    pourcentagedureejouee = 0

                try:
                    self.frameRandomPlay.slider_duration.setPercent(pourcentagedureejouee)
                except KeyError:
                    pass

                try:
                    self.frameRandomPlay.labelduree_jouee.setLabel(label=outils.getInHMS(dico['time']))
                except KeyError:
                    pass

                try:
                    self.frameRandomPlay.labelduree_fin.setLabel(label=outils.getInHMS(dico['duration']))
                except KeyError:
                    self.frameRandomPlay.labelduree_fin.setLabel(label=outils.getInHMS(0.0))

                playlistatraiter = listedechamps[1:]
                debug('playlist à traiter : ' + str(playlistatraiter), xbmc.LOGNOTICE)

                for champs in playlistatraiter:
                    debug('champs : ' + str(champs), xbmc.LOGNOTICE)

                    indexdeID = champs.find('|id:')
                    indexdeTitre = champs.find('|title:')
                    titre = champs[indexdeTitre + 7:]
                    track_id = champs[indexdeID + 4: indexdeTitre]
                    playlist_index = champs[0: indexdeID]
                    debug('index : ' + playlist_index, xbmc.LOGNOTICE)

                    if playlist_index == '0' :
                        debug('Titre : ' + titre + ' - Titre_index_O : ' + Titre_of_index_0 , xbmc.LOGNOTICE)
                        if not ( Titre_of_index_0 == titre ):
                            self.frameRandomPlay.listMenu_playlist.reset()
                            Titre_of_index_0 =  titre
                            flagResetListe = True

                    tracktampon = xbmcgui.ListItem()
                    tracktampon.setLabel(titre)
                    tracktampon.setProperty('track_id', track_id)
                    tracktampon.setProperty('index', playlist_index)
                    #nameOfFileArtwork = self.get_artwork(playlist_index, track_id)
                    #tracktampon.setArt({'thumb': nameOfFileArtwork})

                    size_of_listMenu_playlist = self.frameRandomPlay.listMenu_playlist.size()

                    if int(playlist_index) >= size_of_listMenu_playlist:
                        nameOfFileArtwork = self.get_artwork(index=playlist_index, artwork_track_id=track_id)
                        tracktampon.setArt({'thumb': nameOfFileArtwork})
                        self.frameRandomPlay.listMenu_playlist.addItem(tracktampon)
                        # put again the playing item because lost by addItem
                        self.frameRandomPlay.listMenu_playlist.selectItem(int(playlist_current_index_title))

                # once the list done, fil the artwork thumbs
                if ( flagResetListe == True ):
                    flagResetListe = False
                    for i in range (0 , size_of_listMenu_playlist) :
                        itemList = self.frameRandomPlay.listMenu_playlist.getListItem(i)
                        track_id = itemList.getProperty('track_id')
                        nameOfFileArtwork = self.get_artwork(index=i, artwork_track_id=track_id)
                        itemList.setArt({'thumb':nameOfFileArtwork})

            except ValueError:
                pass

            if not self.frameRandomPlay.threadRunning:
                debug(' jivelette.threadRunning is not True ', xbmc.LOGNOTICE)
                self.Abonnement.clear()

            if not old_current_index_title == playlist_current_index_title:
                self.frameRandomPlay.listMenu_playlist.selectItem(int(playlist_current_index_title))
                old_current_index_title = playlist_current_index_title

            self.InterfaceCLI.viderLeBuffer()
            self.InterfaceCLI.sendtoCLISomething('album ?')
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            album = reponse.split('album|').pop()
            #self.frameRandomPlay.labelAlbum.reset()
            self.frameRandomPlay.labelAlbum.setLabel(label='[B]' + album + '[/B]')

            self.InterfaceCLI.viderLeBuffer()
            self.InterfaceCLI.sendtoCLISomething('artist ?')
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            artist = reponse.split('artist|').pop()
            #self.frameRandomPlay.labelArtist.reset()
            self.frameRandomPlay.labelArtist.setLabel(label='[B]' + artist + '[/B]')

            self.InterfaceCLI.viderLeBuffer()
            self.InterfaceCLI.sendtoCLISomething('title ?')
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            artist = reponse.split('title|').pop()
            #self.frameRandomPlay.labelTitle.reset()
            self.frameRandomPlay.labelTitle.setLabel(label='[B]' + artist + '[/B]')
         # end loop While

        debug('End of Boucle in Update random mix in frameMenu', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        debug('Send resiliersouscription in A update_random_mix() in frameMenu', xbmc.LOGNOTICE)
        self.InterfaceCLI.viderLeBuffer()
    # Fin fonction update_random_mix_Playlist

    # Reminder :
    # racine -> branches -> feuilles -> fleurs ->  etamines
    # root ->   branchs ->  leaves - >  flowers -> stamens

    def les_menus_feuilles_Extras(self, numeroItemSelectionBranche):
        outils.functionNotYetImplemented()

    def get_artwork(self, index , artwork_track_id):
        '''
                fetch the image artwork  or icon from server or somewhere in tne net
                and store it in a temporay directory .
        '''
        filename = 'artwork.image_' + str(index) + '_' + str(artwork_track_id) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)
        debug('filename artwork : ' + str(completeNameofFile), xbmc.LOGNOTICE)
        # http://<server>:<port>/music/<track_id>/cover.jpg
        urltoopen = 'http://' + self.lmsip + ':' + self.lmswebport + '/music/' + artwork_track_id + '/cover.jpg'

        try:
            urllib.urlretrieve(urltoopen, completeNameofFile)
        except IOError:
            pass

        debug('nom du fichier image : ' + completeNameofFile, xbmc.LOGNOTICE)

        return completeNameofFile
        # fin fonction fin fonction get_icon, class Plugin_Generique
        # test


    def functionNotPossible(self, menu):
        itemdeListe_3= xbmcgui.ListItem()
        itemdeListe_3.setLabel('Server has not')
        menu.addItem(itemdeListe_3)
        itemdeListe_4 = xbmcgui.ListItem()
        itemdeListe_4.setLabel('this capability')
        menu.addItem(itemdeListe_4)

    # quelques fonctions communes à d'autres répétées ici
    #
    def pause_play(self):
        #self.get_playerid()
        #self.get_ident_server()
        #self.connectInterface()

        if not self.flagStatePause:
            self.bouton_pause.setVisible(True)
            self.flagStatePause = True
            requete = self.playerid + ' pause 1'
            self.InterfaceCLI.viderLeBuffer()
            self.InterfaceCLI.sendtoCLISomething(requete)
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            del reponse

        else:

            requete = self.playerid + ' pause 0'
            self.InterfaceCLI.viderLeBuffer()
            self.InterfaceCLI.sendtoCLISomething(requete)
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            if 'pause' in reponse:
                self.bouton_pause.setVisible(False)
                self.flagStatePause = False
            del reponse


    def promptVolume(self):
        volumeFrame = outils.VolumeFrameChild()
        volumeFrame.doModal()
        del volumeFrame

    def promptContextMenu(self):
        contextMenuFrame = outils.ContextMenuFrameChild()
        contextMenuFrame.doModal()
        del contextMenuFrame
