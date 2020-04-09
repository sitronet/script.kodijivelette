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
from resources.lib.ConnexionClient import InterfaceCLIduLMS
from resources.lib.outils import KODI_VERSION
from resources.lib.Ecoute import Souscription
from resources.lib import Ecoute, FramePLaying, FramePlaylist, outils, Plugin
import json
#from singleton_decorator import singleton

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

    #__language__ = xbmc.Language(os.getcwd()).getLocalizedString
    __settings__ = xbmcaddon.Addon(id=ADDONID)
    __language__ = __settings__.getLocalizedString

    # print __language__(32001)

    TIME_OF_LOOP_SUBSCRIBE = Ecoute.TIME_OF_LOOP_SUBSCRIBE

    # screen 16:9 so to have grid square fix to 16-9 on 1280 x 720 max of pyxbmct
    SIZE_WIDTH_pyxbmct = 1280
    SIZE_HEIGHT_pyxbmct = 720
    SEIZE = 16 * 4  #32 16 option
    NEUF =   9 * 4  #18 or 9

    #savepath = '/tmp/'
    savepath = xbmc.translatePath('special://temp')

    def translation(message_id, default=False):

        try:
            if not __language__(message_id) and default:
                #xbmc.log('language default', xbmc.LOGNOTICE)
                xbmc.log( 'traduction absente : ' + str(message_id) , xbmc.LOGNOTICE)
                return default
            xbmc.log('language traduit', xbmc.LOGNOTICE)
            xbmc.log( __language__(message_id), xbmc.LOGNOTICE)
            #xbmc.log(ADDON.getLocalizedString(message_id), xbmc.LOGNOTICE)
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
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','fond-noir.jpg'))


pyxbmct.addonwindow.skin = MySkin()


# todo : test , try to catch the requete from FrameList (communicate between frame) , is it possible ?

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
class fenetreMenu(pyxbmct.AddonFullWindow):

    def __init__(self,*args, **kwargs):
        title = args[0]
        super(fenetreMenu, self).__init__(title)

        self.Window_is_playing  = 0
        self.flagContextMenu = False
        self.flagVolumeDisplay = False
        self.flagStatePause = False
        self.recevoirEnAttente = threading.Event()
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

        xbmc.log('Starting Frame for the menu  with window  pyxbmct ', xbmc.LOGNOTICE)
        xbmc.log('special temp is : ' + str(savepath) , xbmc.LOGNOTICE )

        self.image_dir = ARTWORK    # path to pictures used in the program

        self.startSqueeze()
        self.testEnvironnement()

        self.geometrie()
        self.defineControlMenus()
        self.putControlElements()
        self.welcome()
        self.set_navigation_lateral()
        self.connexionEvent()
        self.population()

        self.backgroundFonction()

        self.connectControlElements()

        xbmc.log('FIN de _init_', xbmc.LOGDEBUG)


    def onAction(self, action):
        """
        Catch button actions.

        ``action`` is an instance of :class:`xbmcgui.Action` class.
        """
        self.WindowPlaying_current = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre en sortie dans methode onAction n° : ' + str(self.WindowPlaying_current), xbmc.LOGDEBUG)
        xbmc.log('fenetre enregistrée dans methode now_is_playing n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        if action == ACTION_PREVIOUS_MENU:
            # todo : à redéfinir si au milieu des menus
            # pour ne pas sortir
            # sortir uniquement si menu racine ou init
            xbmc.log('Action Previous_menu' , xbmc.LOGNOTICE)
            self.quit()

        elif action == ACTION_NAV_BACK:
            xbmc.log('Action nav_back' , xbmc.LOGNOTICE)
            self.quit()

        elif action == xbmcgui.ACTION_CONTEXT_MENU:     # it's a strange icon key on my remote
            xbmc.log('Action ContextMenu', xbmc.LOGNOTICE)
            if not self.flagContextMenu:
                self.label_ContextFuture.setLabel('developpement futur')
                self.label_ContextFuture.setVisible(True)
                self.flagContextMenu = True
            else:
                self.label_ContextFuture.setVisible(False)
                self.flagContextMenu = False

        elif action == ACTION_PAUSE:  # currently it's the space bar on my remote
            xbmc.log('Action Pause', xbmc.LOGNOTICE)
            self.pause_play()

        elif action == ACTION_PLAY or action == ACTION_PLAYER_PLAY:
            xbmc.log('Action Play', xbmc.LOGNOTICE)
            self.pause_play()

        elif action == ACTION_VOLUME_UP:    # it's the volume key Vol+  on my remote
            self.setVolume('UP')

        elif action == ACTION_VOLUME_DOWN:  # it's the volume key Vol-  on my remote
            self.setVolume('DOWN')


        else:
            xbmc.log('else condition onAction ' + repr(action)  , xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)

    def quit(self):
        xbmc.log('quit asked - Exit program  0 fonction quit() .', xbmc.LOGNOTICE)
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
            xbmc.log('quit done - Exit program  0 fonction quit() .', xbmc.LOGNOTICE)
            self.close()
        else:
            pass


    #def onControl(self, control):
    #    xbmc.log("Window.onControl(control=[%s])"%control , xbmc.LOGNOTICE)

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
        xbmc.log('path : ' + str(sys.path) , xbmc.LOGNOTICE)
        xbmc.log('test environnement : ' + str(os.tmpfile()) + ' - '+ str(os.uname()) , xbmc.LOGNOTICE)
        leSystem = platform.system()
        xbmc.log( 'System : ' + str(leSystem) , xbmc.LOGNOTICE )

    def geometrie(self):
        '''set the geometry of the screen to place later elements and controls (list button image etc...)'''
        SIZESCREEN_HEIGHT = xbmcgui.getScreenHeight()            # exemple  # 1080
        SIZESCREEN_WIDTH = xbmcgui.getScreenWidth()                         # 1920

        # replaced by pyxbmct but need for the size cover until the fix
        self.GRIDSCREEN_Y, Reste = divmod(SIZESCREEN_HEIGHT, 10)            # 108
        self.GRIDSCREEN_X, Reste = divmod(SIZESCREEN_WIDTH, 10)             # 192

        self.screenx = SIZESCREEN_WIDTH
        self.screeny = SIZESCREEN_HEIGHT
        xbmc.log('Size of Frame Menu: ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        if self.screenx > SIZE_WIDTH_pyxbmct:
            self.screenx = SIZE_WIDTH_pyxbmct
            self.screeny = SIZE_HEIGHT_pyxbmct

        #pyxbmct :
        self.setGeometry(self.screenx  , self.screeny , NEUF, SEIZE)
        xbmc.log('Size of Frame Menu fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        # sizecover must be  a square
        #SIZECOVER_X  = int(self.GRIDSCREEN_X * 2.5)  # need to ask artWork size from server, adapt to the size screen
        SIZECOVER_X = int(self.screenx / SEIZE * 28 )
        self.sizecover_x = SIZECOVER_X
        #SIZECOVER_Y = self.GRIDSCREEN_Y * 3  # and reserve a sized frame to covers,attention SIZECOVER_X != SIZECOVER_Y
        xbmc.log('Taille pochette : ' + str(SIZECOVER_X) + ' x ' + str(SIZECOVER_X) , xbmc.LOGNOTICE)

        self.image_dir = ARTWORK    # path to pictures used in the program (future development, todo)

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


    def backgroundFonction(self):

        # button pause :
        self.bouton_pause = pyxbmct.Button(label='', focusTexture=self.image_button_pause,
                                           noFocusTexture=self.image_button_pause)
        self.placeControl(control=self.bouton_pause, row=NEUF / 2, column=int(SEIZE / 2) - 5, rowspan=6, columnspan=6)
        self.bouton_pause.setVisible(False)
        self.bouton_play = pyxbmct.Button(label='', focusTexture=self.image_button_play, noFocusTexture='')
        self.placeControl(self.bouton_play, row=NEUF / 2, column=(SEIZE / 2) - 2, rowspan=6, columnspan=6)
        self.bouton_play.setVisible(False)

        # Slider Volume :
        self.label_volume = pyxbmct.Label('', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(control=self.label_volume, row=(NEUF / 2) - 2, column=(SEIZE / 2) - 15, rowspan=2,
                          columnspan=30)
        self.slider_volume = pyxbmct.Slider(textureback=self.textureback_slider_volume,
                                            texture=self.texture_slider_volume,
                                            texturefocus=self.textureback_slider_volume, orientation=xbmcgui.HORIZONTAL)
        self.placeControl(control=self.slider_volume, row=NEUF / 2, column=(SEIZE / 2) - 15, rowspan=3, columnspan=30)
        self.label_volume.setVisible(False)
        self.slider_volume.setVisible(False)

        # future
        self.label_ContextFuture = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.label_ContextFuture, NEUF / 2, (SEIZE / 2) - self.espace_col, 3 * self.espace_row, self.espace_col * 2)
        self.label_ContextFuture.setVisible(False)



    def defineControlMenus(self):
        ''' Fix the size of itemlists in menus lists'''

        self.ListePourInitialisationServerPlayers = [ translation(32920 , 'Init the Server' ),
                                                      translation(32921 , 'Quit the program' )]

        self.listeRacinePourMenuRacine = [ translation(32040 , 'Now Playing'),
                                           translation(32041 , 'My Music'),
                                           translation(32042 , 'I-Radio' ),
                                           translation(32043 , 'My Apps'),
                                           translation(32044 , 'Favorites'),
                                           translation(32045 , 'Extras'),
                                           translation(32046 , 'Quit') ]

        self.listeMyMusicPourMenuMyMusic = [
                                        translation(32050 , 'Album Artists'),
                                        translation(32051 , 'All Artists'),
                                        translation(32052 , 'Composers'),
                                        translation(32053 , 'Albums'),
                                        translation(32054 , 'Compilations'),
                                        translation(32055 , 'Genres'),
                                        translation(32056 , 'Years'),
                                        translation(32057 , 'New Music'),
                                        translation(32058 , 'Random Mix'),
                                        translation(32059 , 'Music Folder'),
                                        translation(32060 , 'Playlists'),
                                        translation(32061 , 'Search'),
                                        translation(32062 , 'Remote Music Librairies') ]

        self.listeExtraPourMenuExtras = [ translation(32072 , 'players'),
                                          translation(32073 , 'Music Source') ,
                                          translation(32074 , 'Don\'t stop the music') ]

        self.listMenu_Initialisation = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _itemHeight=40)

        self.listMenu_Racine = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _itemHeight=40)

        self.listMenu_MyMusic = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 38 , _imageHeight = 38 , _itemHeight = 40 )

        self.listMenu_Branches  = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 38 , _imageHeight = 38 , _itemHeight = 40 )

        # we keep it for later (settings and so)
        self.listMenu_Extras = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)

        # à voir plus tard
        self.listMenu_Feuilles = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
        self.listMenu_Feuilles_all_Artists = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth=38, _imageHeight=38, _itemHeight=40)
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


        row_depart = 1
        self.espace_row = 30
        self.espace_col = 10
        hauteur_menu = 25
        col_depart_menu_branche = self.espace_col + 1
        row_hauteur_menu_branche = 30
        col_largeur_menu_branche = 15
        col_depart_menu_feuille = col_depart_menu_branche + col_largeur_menu_branche + 2
        col_largeur_menu_feuille = col_largeur_menu_branche + 10
        row_hauteur_menu_feuille = row_hauteur_menu_branche

        # init
        
        self.placeControl(self.listMenu_Initialisation,  NEUF / 2  ,  (SEIZE / 2 ) - self.espace_col  , self.espace_row, self.espace_col * 2 )

        self.placeControl(self.listMenu_Racine , row_depart , 0, self.espace_row, self.espace_col)

        # Add items to the list
        self.listMenu_Initialisation.addItems(self.ListePourInitialisationServerPlayers)

        self.listMenu_Racine.addItems(self.listeRacinePourMenuRacine)
        self.listMenu_Extras.addItems(self.listeExtraPourMenuExtras)

        # I try to paste the control here if not raise un error
        self.placeControl(self.listMenu_MyMusic, row_depart, col_depart_menu_branche, \
                          row_hauteur_menu_branche, col_largeur_menu_branche)

        self.placeControl(self.listMenu_Branches , row_depart, col_depart_menu_branche, \
                          row_hauteur_menu_branche, col_largeur_menu_branche)

        self.placeControl(self.listMenu_Extras, row_depart , col_depart_menu_branche, \
                          row_hauteur_menu_branche, col_largeur_menu_branche)


        self.placeControl(self.listMenu_Feuilles, row_depart, col_depart_menu_feuille, \
                          row_hauteur_menu_feuille,col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_all_Artists, row_depart, col_depart_menu_feuille, \
                          row_hauteur_menu_branche,col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_RandomMix, row_depart, col_depart_menu_feuille, \
                          row_hauteur_menu_branche,col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Feuilles_Extras, row_depart, col_depart_menu_feuille, \
                          row_hauteur_menu_branche,col_largeur_menu_feuille)

        self.placeControl(self.listMenu_Fleur, row_depart , col_depart_menu_feuille + col_largeur_menu_branche  , \
                          row_hauteur_menu_branche , col_largeur_menu_branche )



    def connectControlElements(self):
        # Connect the list to a function to display which list item is selected.
        # example :
        # self.connect(self.list_Menu, lambda: xbmc.executebuiltin('Notification(Note!,{0} selected.)'.format(
        #    self.list_Menu.getListItem(self.list_Menu.getSelectedPosition()).getLabel())))

        # init
        #self.connect(self.listMenu_Initialisation, self.navigationFromMenuInitialisation())
        #
        self.connect(self.listMenu_Racine, self.navigationFromMenuRacine)
        self.connect(self.listMenu_MyMusic, self.navigationFromMenusMyMusic)
        self.connect(self.listMenu_Branches, self.navigationFromMenuBranche)
        self.connect(self.listMenu_Feuilles, self.navigationFromMenuFeuilles)
        self.connect(self.listMenu_Feuilles_all_Artists, self.navigationFromMenuFeuilles_all_Artists)
        self.connect(self.listMenu_Feuilles_RandomMix, self.navigationFromMenuFeuilles_RandomMix)
        self.connect(self.listMenu_Extras, self.navigationFromMenuBrancheExtras)
        self.connect(self.listMenu_Feuilles_Extras, self.navigationFromMenuFeuillesExtras)

        self.connect(self.listMenu_Fleur, self.launchPlayingItem)
        # etcoetera...
        # init
        self.connect(self.listMenu_Initialisation, self.navigationFromMenuInitialisation)

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
        self.listMenu_Feuilles_RandomMix.controlLeft(self.listMenu_MyMusic)

        self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)
        self.listMenu_Feuilles_Extras.controlLeft(self.listMenu_Extras)


        self.listMenu_Feuilles.controlRight(self.listMenu_Fleur)
        self.listMenu_Fleur.controlLeft(self.listMenu_Feuilles)

        # todo : à revoir pour les autre menus (radios , favorites etc...

        # Set initial focus
        #self.setFocus(self.listMenu_Racine)
        self.setFocus(self.listMenu_Initialisation)

    def move_through_sub_menu(self):
        # on verra plus tard si nécessaire Todo
        self.itemSelectionRacine = self.list_Menu.getListItem(self.list_Menu.getSelectedPosition()).getLabel()

    def launchPlayingNowandOthersCommands(self, title):
        '''
        :param title:
        :return:
        '''
        #itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

        self.Abonnement.set()
        self.jivelette = FramePLaying.SlimIsPlaying(title)
        self.jivelette.show()
        time.sleep(0.5)
        self.update_now_is_playing()
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

        xbmc.log('launch to play : ' + labelajouer + ' ' + cmd + ' playlist play item_id:' + item_id , xbmc.LOGNOTICE  )
        if audio_type == 'audio' and hasitems == '0':
            # send the command to play the item_id
            self.InterfaceCLI.sendtoCLISomething( cmd + ' playlist play item_id:' + item_id )
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            time.sleep(0.5) # let's the time to retrieve the stream to get the cover
            # then launch the frame Now_is_playing
            # self.command here become the title of the Frame
            if  '|local|playlist|play|item_id:' in reponse:
                self.launchPlayingNowandOthersCommands(labelajouer)

        else:
            notFinish = Plugin.Plugin_Generique()
            notFinish.functionNotYetImplemented()

    def navigationFromMenuInitialisation(self):
        try:
                self.listMenu_Initialisation.setVisible(True)
                self.listMenu_Racine.setVisible(True)
                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
        except:
                pass
        itemSelection = self.listMenu_Initialisation.getListItem(self.listMenu_Initialisation.getSelectedPosition()).getLabel()
        itemPosition = self.listMenu_Initialisation.getSelectedPosition()
        xbmc.log('item is : ' + str(itemSelection), xbmc.LOGNOTICE)
        if itemSelection ==  translation(32920 , 'Init the Server'):
            self.initialisationServeurPlayeur()
            self.testCapaciteServeur()
            self.set_artwork_size()
            #self.listMenu_Initialisation.setVisible(False)
            #self.removeControl(self.listMenu_Initialisation)
            #self.getFocus(self.listMenu_Racine)


        elif itemSelection == translation(32921 , 'Quit the program' ):
            self.quit()

        else :
            self.playerid = self.dictionnairedesplayers[itemPosition + 1]['playerid']
            outils.WhatAreThePlayers.playerSelection = self.playerid
            try:
                self.listMenu_Initialisation.setVisible(False)
                self.listMenu_Racine.setVisible(True)
                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
                self.setFocus(self.listMenu_Racine)
                self.Information_label.setVisible(False)
            except:
                pass


    def navigationFromMenuRacine(self):

        itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

        if itemSelectionRacine == translation(32040 , 'Now Playing'):
            # activer frame EcouteEnCours
            self.Abonnement.set() # need to renew subscribe after interupt
            self.jivelette = FramePLaying.SlimIsPlaying(translation(32040, 'Now Playing'))

            self.WindowPlaying = xbmcgui.getCurrentWindowId()
            xbmc.log('fenetre en cours n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)

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
            self.setFocus(self.listMenu_Branches)

            new_radio = Plugin.Plugin_Generique(self)
            self.liste_du_menu_branche_des_plugins = new_radio.le_menu_branche('radios')
            self.setFocus(self.listMenu_Branches)


        elif itemSelectionRacine == translation(32043 , 'My Apps'):

            if self.can_myapps:
                self.listMenu_Branches.reset()
                self.setFocus(self.listMenu_Branches)

                new_apps = Plugin.Plugin_Generique(self)
                self.liste_du_menu_branche_des_plugins = new_apps.le_menu_branche('apps')
                self.setFocus(self.listMenu_Branches)

            else:
                self.functionNotPossible(menu=self.listMenu_Branches)

        elif itemSelectionRacine == translation(32044 , 'Favorites'):
            if self.can_favorites:
                self.listMenu_Branches.reset()

                new_favorites = Plugin.Plugin_Favorites(self)
                self.liste_du_menu_branche_des_plugins = new_favorites.le_menu_branche('favorites')
            else:
                self.functionNotPossible(menu=self.listMenu_Branches)

        elif  itemSelectionRacine == translation(32045 , 'Extras'):
            xbmc.log('selection Extras' , xbmc.LOGNOTICE)
            self.listMenu_Extras.reset()
            self.listMenu_Extras.addItems(self.listeExtraPourMenuExtras)
            self.setFocus(self.listMenu_Extras)
            #self.navigationFromMenuBrancheExtras()

        elif itemSelectionRacine == translation(32046 , 'Quit'):
            xbmc.log('menu Quit requested', xbmc.LOGNOTICE)
            self.quit()

    def navigationFromMenusMyMusic(self):

        self.itemSelectionBranche = self.listMenu_MyMusic.getListItem(
                            self.listMenu_MyMusic.getSelectedPosition()).getLabel()
        self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
        xbmc.log('position curseur sur menu après connect : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)
        self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
        NumeroItemSelectionBranche = self.listMenu_MyMusic.getSelectedPosition()
        try:

                self.listMenu_Racine.setVisible(True)
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(True)

                self.listMenu_Fleur.setVisible(False)
        except:
                pass

        if self.itemSelectionBranche == translation(32051 , 'All Artists'):
            try:
                self.listMenu_Racine.setVisible(True)
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(True)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Artists)
            self.listMenu_Feuilles_all_Artists.controlLeft(self.listMenu_MyMusic)

            if not self.all_Artists_populated:
                new_music = Plugin.MyMusic(self)
                new_music.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche)

        elif self.itemSelectionBranche == translation(32058 , default='Random Mix'):

            try:
                self.listMenu_Racine.setVisible(True)
                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(True)
                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            if not self.can_randomplay:
                # the server is not able  -> print not possible
                self.functionNotPossible(self.origine.listMenu_Fleur)
                return

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
            #todo :  write the other actions from the menu_music
            self.listMenu_Feuilles_RandomMix.setVisible(False)
            self.listMenu_Feuilles_all_Artists.setVisible(False)
            self.listMenu_Feuilles.setVisible(True)
            self.listMenu_Feuilles.reset()
            self.functionNotYetImplemented(self.listMenu_Feuilles)

    def navigationFromMenuBranche(self):

        self.itemSelectionBranche = self.listMenu_Branches.getListItem(
            self.listMenu_Branches.getSelectedPosition()).getLabel()

        NumeroItemSelectionBranche = self.listMenu_Branches.getSelectedPosition()

        # affichage en bas écran dans un label le menu en cours
        self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
        xbmc.log('position curseur sur menu après connect : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)

        self.listMenu_Racine.controlRight(self.listMenu_Branches)

        if self.itemSelectionRacine == translation(32041 , 'My Music'):
            # it must not be possible as we are in menu Branch and not in menu MyMusic
            pass

        if self.itemSelectionRacine == translation(32042 , 'I-Radio' ) or \
                self.itemSelectionRacine == translation(32043 , 'My Apps'):

            try:
                # self.listMenu_Branches.reset() # à voir plus tard si on reset les lists menu
                self.listMenu_Racine.setVisible(True)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(True)
                self.listMenu_Extras.setVisible(False)
                self.listMenu_Feuilles.setVisible(True)
                self.listMenu_Feuilles_all_Artists.setVisible(False)

                self.listMenu_Fleur.setVisible(False)
            except:
                pass

            new_feuille = Plugin.Plugin_Generique(self)

        elif self.itemSelectionRacine == translation(32044 , 'Favorites'):

            new_feuille = Plugin.Plugin_Favorites(self)

        new_feuille.le_menu_feuille(numeroItemSelectionBranche=NumeroItemSelectionBranche)

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

        xbmc.log('label dans menu Feuille : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        xbmc.log('id dans menu Feuille : ' + itemIdSelection, xbmc.LOGNOTICE)
        xbmc.log('artist dans menu Feuille : ' + artist , xbmc.LOGNOTICE)
        xbmc.log('hasitems dans menu Feuille : ' + hasitems, xbmc.LOGNOTICE)
        xbmc.log('numéro dans menu Feuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

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
            xbmc.log('id item artist : ' + str(itemSelection) , xbmc.LOGNOTICE)
            itemalternate = self.listMenu_Feuilles.getSelectedItem().getProperty('artist_id')
            xbmc.log('id item artist alternate : ' + str(itemalternate) , xbmc.LOGNOTICE)

            self.listMenu_MyMusic.setVisible(True)

            if itemSelection:
                new_menu = Plugin.MyMusic(self)
                new_menu.le_menu_fleurs(itemSelection)

        else:
            new_menu = Plugin.Plugin_Generique(self)
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

        xbmc.log('label dans menu Feuille All Artists : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
        xbmc.log('id dans menu Feuille All Artists : ' + itemIdSelection, xbmc.LOGNOTICE)
        xbmc.log('artist dans menu Feuille All Artists : ' + artist , xbmc.LOGNOTICE)
        xbmc.log('hasitems dans menu Feuille All Artists : ' + hasitems, xbmc.LOGNOTICE)
        xbmc.log('numéro dans menu Feuille All Artists : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

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
        self.listMenu_Fleur.setVisible(True)

        #self.setFocus(self.listMenu_Fleur)
        itemSelection = self.listMenu_Feuilles_all_Artists.getListItem(
            self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('artist_id')
        xbmc.log('id item artist : ' + str(itemSelection) , xbmc.LOGNOTICE)
        itemalternate = self.listMenu_Feuilles_all_Artists.getSelectedItem().getProperty('artist_id')
        xbmc.log('id item artist alternate : ' + str(itemalternate) , xbmc.LOGNOTICE)

        new_menu = Plugin.MyMusic(self)
        new_menu.le_menu_fleurs(itemSelection)

    def navigationFromMenuFeuilles_RandomMix(self):
        # reset the screen invisible
        self.listMenu_Racine.setVisible(True)
        self.listMenu_MyMusic.setVisible(True)
        self.listMenu_Branches.setVisible(False)
        self.listMenu_Extras.setVisible(False)
        self.listMenu_Feuilles.setVisible(False)
        self.listMenu_Feuilles_all_Artists.setVisible(False)
        self.listMenu_Feuilles_RandomMix.setVisible(True)
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

        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()

        self.Abonnement.set()
        self.frameRandomPlay = FramePlaylist.PlaylistPlugin(translation(32040, 'Now playing ') + ' : ' + title)
        self.frameRandomPlay.show()
        self.frameRandomPlay.listMenu_playlist.reset()
        self.update_random_mix_Playlist()

    def navigationFromMenuBrancheExtras(self):

        xbmc.log(' entrée dans le_menus_branche_extras', xbmc.LOGNOTICE)

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
            self.functionNotYetImplemented(self.listMenu_Feuilles_Extras)
        elif NumeroItemSelectionBranche == 2:
            self.listMenu_Feuilles_Extras.reset()
            self.functionNotYetImplemented(self.listMenu_Feuilles_Extras)

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

            # example to getProperty  :
            #hasitems = self.listMenu_Feuilles.getListItem(
            #    self.listMenu_Feuilles.getSelectedPosition()).getProperty('hasitems')

            playerid = self.listMenu_Feuilles_Extras.getListItem(
                self.listMenu_Feuilles_Extras.getSelectedPosition()).getProperty('playerid')
            etat = self.listMenu_Feuilles_Extras.getListItem(
                self.listMenu_Feuilles_Extras.getSelectedPosition()).getProperty('power')
            if etat == '0':
                #<playerid> power <0|1|?|>
                requete = playerid + ' power 1'
            else:
                requete = playerid + ' power 0'

            self.InterfaceCLI.sendtoCLISomething(requete)
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            del reponse

            #todo : activate deactivate player won't work ? because dictionnaryplayer is not updated
            # l'état des players a changé , réinitialisation du dictionnaire des players

            self.Players = outils.WhatAreThePlayers()
            self.dictionnairedesplayers = dict()
            self.dictionnairedesplayers = self.Players.recherchedesPlayers(self.InterfaceCLI, self.recevoirEnAttente)
            # recherche d'un player actif et si actif vrai . actif = isplaying
            self.actif, index_dictionnairedesPlayers, self.playerid = self.Players.playerActif(
                self.dictionnairedesplayers)

    def listMenu_Radios_update(self): #todo  pour test à supprimer
        xbmc.log('test event' , xbmc.LOGNOTICE)
        pass

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
                labeltemp = labeltemp + ' : ' + translation(32800 , 'Activate Player' )
            else:
                labeltemp = labeltemp + ' : ' + translation(32801 , 'Deactivate Player')

            menuunplayer.setLabel(labeltemp)
            #xbmc.log('populate player menu' + labeltemp + unplayer['playerid']  , xbmc.LOGNOTICE) # ! could be unicode
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
        row_depart = 1
        self.espace_row = 20
        self.espace_col = 10
        hauteur_menu = 25
        col_depart_menu_branche = self.espace_col + 1
        row_hauteur_menu_branche = 30
        col_largeur_menu_branche = 15
        # Update list_item label when navigating through the list.
        self.itemSelectionRacine = ''
        self.itemSelectionBranche = ''
        self.itemSelectionFeuille = ''
        self.itemSelectionFleur = ''

        self.itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

        # affichage en bas écran dans un label le menu en cours
        #self.list_racine_label.setLabel('# ' + self.itemSelectionRacine)
        xbmc.log( 'position curseur sur menu : ' + self.itemSelectionRacine, xbmc.LOGDEBUG)

        try:
            if self.getFocus() == self.listMenu_Initialisation:
                self.itemSelectionInitialisation = self.listMenu_Initialisation.getListItem(
                    self.listMenu_Initialisation.getSelectedPosition()).getLabel()
                self.list_racine_label.setLabel('::' + self.itemSelectionInitialisation)
                xbmc.log('position curseur sur menu init : ' + self.itemSelectionInitialisation, xbmc.LOGNOTICE)

            if self.getFocus() == self.listMenu_Racine:

                # on récupère le label de l'item du menu principal sur lequel on est positionné
                self.itemSelectionRacine = self.listMenu_Racine.getListItem(self.listMenu_Racine.getSelectedPosition()).getLabel()

                # affichage en bas écran dans un label le menu en cours
                self.list_racine_label.setLabel('::' + self.itemSelectionRacine)
                xbmc.log( 'position curseur sur menu : ' + self.itemSelectionRacine, xbmc.LOGNOTICE)
                # remise à blanc des sous labels
                self.list_item_branche_label.setLabel('')
                self.list_item_feuille_label.setLabel('')

                if self.itemSelectionRacine == translation(32041 , 'My Music'): # condition always true. never mind
                                                           # we will delete them later after try et rewriting the code

                    try:
                        self.placeControl(self.listMenu_MyMusic, row_depart,
                                                col_depart_menu_branche,
                                                row_hauteur_menu_branche,
                                                col_largeur_menu_branche)
                    except:
                        pass
                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(True)
                    self.listMenu_Branches.setVisible(False)
                    self.listMenu_Extras.setVisible(False)

                    self.listMenu_Feuilles.setVisible(False)
                    self.listMenu_Feuilles_all_Artists.setVisible(False)
                    self.listMenu_Feuilles_RandomMix.setVisible(False)
                    self.listMenu_Feuilles_Extras.setVisible(False)

                    self.listMenu_Fleur.setVisible(False)

                    try:
                        self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                        self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                    except:
                        pass

                elif self.itemSelectionRacine == translation(32042 , 'I-Radio' ):

                    try:
                        self.placeControl(self.listMenu_Branches, row_depart,
                                      col_depart_menu_branche,
                                      row_hauteur_menu_branche,
                                      col_largeur_menu_branche)
                    except:
                        pass

                    try:
                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
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

                elif self.itemSelectionRacine == translation(32043 , 'My Apps'): 

                    try:
                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)

                    except:
                        pass

                    try:
                        self.placeControl(self.listMenu_Branches, row_depart,
                                      col_depart_menu_branche,
                                      row_hauteur_menu_branche,
                                      col_largeur_menu_branche)
                    except:
                        pass

                elif self.itemSelectionRacine == translation(32044 , 'Favorites'):

                    try:
                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(True)
                        self.listMenu_Extras.setVisible(False)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)
                    except:
                        pass

                    try:
                        self.placeControl(self.listMenu_Branches, row_depart,
                                      col_depart_menu_branche,
                                      row_hauteur_menu_branche,
                                      col_largeur_menu_branche)
                    except:
                        pass

                elif self.itemSelectionRacine == translation(32045 , 'Extras'):    

                    try:
                        self.placeControl(self.listMenu_Extras, row_depart,
                                      col_depart_menu_branche,
                                      row_hauteur_menu_branche,
                                      col_largeur_menu_branche)
                    except:
                        pass

                    try:
                        #self.listMenu_Extras.reset()
                        self.listMenu_Racine.setVisible(True)

                        self.listMenu_MyMusic.setVisible(False)
                        self.listMenu_Branches.setVisible(False)
                        self.listMenu_Extras.setVisible(True)

                        self.listMenu_Feuilles.setVisible(False)
                        self.listMenu_Feuilles_all_Artists.setVisible(False)
                        self.listMenu_Feuilles_RandomMix.setVisible(False)
                        self.listMenu_Feuilles_Extras.setVisible(False)

                        self.listMenu_Fleur.setVisible(False)
                    except:
                        pass



                elif self.itemSelectionRacine == translation(32046 , 'Quit'):
                    pass

            elif self.getFocus() == self.listMenu_MyMusic:

                self.listMenu_Racine.setVisible(True)

                self.listMenu_MyMusic.setVisible(True)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(False)

                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Feuilles_Extras.setVisible(False)

                self.listMenu_Fleur.setVisible(False)

                # on récupère le label de l'item sur lequel on est positionné
                itemSelectionBranche = self.listMenu_MyMusic.getListItem(
                    self.listMenu_MyMusic.getSelectedPosition()).getLabel()
                xbmc.log('position dans menu My Music : ' + itemSelectionBranche, xbmc.LOGDEBUG)
                self.list_item_feuille_label.setLabel('')

                # affichage en bas écran dans un label le menu en cours
                self.list_item_branche_label.setLabel(' :: ' + itemSelectionBranche)

                NumeroItemSelectionBranche = self.listMenu_MyMusic.getSelectedPosition()

                self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                # à xompléter en descendant dans les menus

            elif self.getFocus() == self.listMenu_Branches:

                self.listMenu_Racine.setVisible(True)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(True)
                self.listMenu_Extras.setVisible(False)

                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Feuilles_Extras.setVisible(False)

                self.listMenu_Fleur.setVisible(False)

                self.itemSelectionBranche = self.listMenu_Branches.getListItem(
                    self.listMenu_Branches.getSelectedPosition()).getLabel()

                # affichage en bas écran dans un label le menu en cours
                self.list_item_branche_label.setLabel(':: ' + self.itemSelectionBranche)
                xbmc.log( 'position curseur sur menu : ' + self.itemSelectionBranche, xbmc.LOGNOTICE)
                #remise à blanc des sous-labels
                self.list_item_feuille_label.setLabel('')
                
                self.listMenu_Racine.controlRight(self.listMenu_Branches)

            elif self.getFocus() == self.listMenu_Extras:

                self.listMenu_Racine.setVisible(True)

                self.listMenu_MyMusic.setVisible(False)
                self.listMenu_Branches.setVisible(False)
                self.listMenu_Extras.setVisible(True)

                self.listMenu_Feuilles.setVisible(False)
                self.listMenu_Feuilles_all_Artists.setVisible(False)
                self.listMenu_Feuilles_RandomMix.setVisible(False)
                self.listMenu_Feuilles_Extras.setVisible(False)

                self.listMenu_Fleur.setVisible(False)

                self.listMenu_Racine.controlRight(self.listMenu_Extras)
                self.listMenu_Extras.controlLeft(self.listMenu_Racine)
                self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)


                itemSelectionBranche = self.listMenu_Extras.getListItem(
                    self.listMenu_Extras.getSelectedPosition()).getLabel()
                # affichage en bas écran dans un label le menu en cours
                self.list_item_branche_label.setLabel(' :: ' + itemSelectionBranche)
                xbmc.log('position dans menu Extras : ' + str(itemSelectionBranche), xbmc.LOGNOTICE)
                #remise à blanc
                self.list_item_feuille_label.setLabel('')

                NumeroItemSelectionBranche = self.listMenu_Branches.getSelectedPosition()

                self.les_menus_feuilles_Extras(numeroItemSelectionBranche=NumeroItemSelectionBranche)

            elif self.getFocus() == self.listMenu_Feuilles:

                try:
                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(False)
                    self.listMenu_Branches.setVisible(True)
                    self.listMenu_Extras.setVisible(False)

                    self.listMenu_Feuilles.setVisible(True)
                    self.listMenu_Feuilles_all_Artists.setVisible(False)
                    self.listMenu_Feuilles_RandomMix.setVisible(False)
                    self.listMenu_Feuilles_Extras.setVisible(False)

                    self.listMenu_Fleur.setVisible(False)
                except  :
                    pass

                itemSelectionFeuille = self.listMenu_Feuilles.getListItem(
                    self.listMenu_Feuilles.getSelectedPosition()).getLabel()
                xbmc.log('label dans menu Feuille : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                #remise à blanc sous-label
                self.list_item_fleur_label.setLabel('')
                NumeroItemSelectionFeuille = self.listMenu_Feuilles.getSelectedPosition()
                hasitems = self.listMenu_Feuilles.getListItem(
                    self.listMenu_Feuilles.getSelectedPosition()).getProperty('hasitems')

                xbmc.log('flowers get an hasitem : ' + str(hasitems), xbmc.LOGNOTICE)
                # if hasitem == 1:
                # dig one  more time (no recursive)
                xbmc.log('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

            elif self.getFocus() == self.listMenu_Feuilles_all_Artists:

                try:
                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(True)
                    self.listMenu_Branches.setVisible(False)
                    self.listMenu_Extras.setVisible(False)

                    self.listMenu_Feuilles.setVisible(False)
                    self.listMenu_Feuilles_all_Artists.setVisible(True)
                    self.listMenu_Feuilles_RandomMix.setVisible(False)
                    self.listMenu_Feuilles_Extras.setVisible(False)

                    self.listMenu_Fleur.setVisible(False)
                except  :
                    pass

                itemSelectionFeuille = self.listMenu_Feuilles_all_Artists.getListItem(
                    self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getLabel()
                xbmc.log('label dans menu Feuille All Artists : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                #remise à blanc sous-label
                self.list_item_fleur_label.setLabel('')
                NumeroItemSelectionFeuille = self.listMenu_Feuilles_all_Artists.getSelectedPosition()
                hasitems = self.listMenu_Feuilles_all_Artists.getListItem(
                    self.listMenu_Feuilles_all_Artists.getSelectedPosition()).getProperty('hasitems')

                xbmc.log('flowers get an hasitem : ' + str(hasitems), xbmc.LOGNOTICE)
                # if hasitem == 1:
                # dig one  more time (no recursive)
                xbmc.log('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_all_Artists)
                self.listMenu_Feuilles_all_Artists.controlLeft(self.listMenu_MyMusic)

                # go to the connect lambda function

            elif self.getFocus() == self.listMenu_Feuilles_RandomMix:

                try:
                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(True)
                    self.listMenu_Branches.setVisible(False)
                    self.listMenu_Extras.setVisible(False)

                    self.listMenu_Feuilles.setVisible(False)
                    self.listMenu_Feuilles_all_Artists.setVisible(False)
                    self.listMenu_Feuilles_RandomMix.setVisible(True)
                    self.listMenu_Feuilles_Extras.setVisible(False)

                    self.listMenu_Fleur.setVisible(False)
                except  :
                    pass

                itemSelectionFeuille = self.listMenu_Feuilles_RandomMix.getListItem(
                    self.listMenu_Feuilles_RandomMix.getSelectedPosition()).getLabel()
                xbmc.log('label dans menu Feuille Random mix : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                #remise à blanc sous-label
                self.list_item_fleur_label.setLabel('')

                NumeroItemSelectionFeuille = self.listMenu_Feuilles_RandomMix.getSelectedPosition()
                xbmc.log('NumeroItemSelectionFeuille : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                self.listMenu_Racine.controlRight(self.listMenu_MyMusic)
                self.listMenu_MyMusic.controlLeft(self.listMenu_Racine)
                self.listMenu_MyMusic.controlRight(self.listMenu_Feuilles_RandomMix)
                self.listMenu_Feuilles_RandomMix.controlLeft(self.listMenu_MyMusic)

            elif self.getFocus() == self.listMenu_Feuilles_Extras:

                try:
                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(False)
                    self.listMenu_Branches.setVisible(False)
                    self.listMenu_Extras.setVisible(True)

                    self.listMenu_Feuilles.setVisible(False)
                    self.listMenu_Feuilles_all_Artists.setVisible(False)
                    self.listMenu_Feuilles_RandomMix.setVisible(False)
                    self.listMenu_Feuilles_Extras.setVisible(True)

                    self.listMenu_Fleur.setVisible(False)
                except  :
                    pass

                itemSelectionFeuille = self.listMenu_Feuilles_Extras.getListItem(
                    self.listMenu_Feuilles_Extras.getSelectedPosition()).getLabel()
                xbmc.log('label dans menu Feuille des Extras : ' + itemSelectionFeuille, xbmc.LOGNOTICE)
                self.list_item_feuille_label.setLabel(' :: ' + itemSelectionFeuille)
                #remise à blanc sous-label
                self.list_item_fleur_label.setLabel('')

                NumeroItemSelectionFeuille = self.listMenu_Feuilles_Extras.getSelectedPosition()
                xbmc.log('NumeroItemSelectionFeuilleExtra : ' + str(NumeroItemSelectionFeuille), xbmc.LOGNOTICE)

                self.listMenu_Racine.controlRight(self.listMenu_Extras)
                self.listMenu_Extras.controlLeft(self.listMenu_Racine)
                self.listMenu_Extras.controlRight(self.listMenu_Feuilles_Extras)
                self.listMenu_Feuilles_Extras.controlLeft(self.listMenu_Extras)

            elif self.getFocus() == self.listMenu_Fleur:
                # deleted but keep it for later in case we need it

                itemSelectionFleur = self.listMenu_Fleur.getListItem(
                    self.listMenu_Fleur.getSelectedPosition()).getLabel()
                xbmc.log('label dans menu les fleurs : ' + itemSelectionFleur, xbmc.LOGNOTICE)
                self.list_item_fleur_label.setLabel(' :: ' + itemSelectionFleur)

                NumeroItemSelectionFleur = self.listMenu_Fleur.getSelectedPosition()
                hasitems = self.listMenu_Fleur.getListItem(
                    self.listMenu_Fleur.getSelectedPosition()).getProperty('hasitems')
                # todo
                # if not hasitems play it when connected (press button ok , enter or select)
                # see fonction connect()
                try:
                    self.listMenu_Racine.setVisible(True)

                    self.listMenu_MyMusic.setVisible(False)
                    self.listMenu_Branches.setVisible(True)
                    self.listMenu_Extras.setVisible(False)

                    self.listMenu_Feuilles.setVisible(True)

                    self.listMenu_Fleur.setVisible(True)
                except  :
                    pass
                self.listMenu_Fleur

        except  (RuntimeError, SystemError): # take from original pyxbmct demo code
            pass

    # fin fonction list_Menu_Navigation

    def welcome(self):
        self.Information_label.setLabel( translation(32931, 'Welcome to the most simple Squeeze Box Display : Kodi Jivelette'))


    def initialisationServeurPlayeur(self):

        # use the same list, just remove the previous items (ie init and quit)
        self.listMenu_Initialisation.removeItem(1)
        self.listMenu_Initialisation.removeItem(0)
        self.Information_label.setLabel( translation(32930, 'Select One player in the list below'))
        outils.recherchonsleServeur(self)

        # maintenant nous connaissons le serveur Idem mainBoucle -> todo revoir logique
        # on lance le thread de connexion permanente avec le serveur. # todo retravailler les events

        self.InterfaceCLI = InterfaceCLIduLMS(self.rechercheduserveur.LMSCLIip,
                                              self.recevoirEnAttente,
                                              self.envoiEnAttente,
                                              self.demandedeStop)
        self.InterfaceCLI.start()

        xbmc.log('type InterfaceCLI -> ' + str(type(self.InterfaceCLI)) , xbmc.LOGDEBUG)

        while not self.InterfaceCLI.EtatDuThread:  # on attend que le thread soit bien démarré j'aurais pu utiliser un event ?
            time.sleep(0.1)

        #sorti de la boucle  ok ici c'est bon le thread de connexion a démarré excepté si la connexion n'est pas bonne
        # il faut faire un event pour savoir si tout est ok - TODO
        # plus simple : le thread est-il vivant -> oui, non

        xbmc.log('thread alive -> ' + str(self.InterfaceCLI.is_alive) + ' . type -> ' + str(type(self.InterfaceCLI.is_alive)) , xbmc.LOGDEBUG)

        if not self.InterfaceCLI.is_alive:
            # we cannot be here because the loop above should not break
            xbmc.log('thread is not alive -> error 33 ' , xbmc.LOGDEBUG)
            exit(33)

        # start here the communication with server througth the self.InterfaceCLI previously started
        # first is to know the players :

        # ici on va couper pour faire une fonction de recherche des players
        self.Players = outils.WhatAreThePlayers()
        self.dictionnairedesplayers = dict()
        self.dictionnairedesplayers = self.Players.recherchedesPlayers(self.InterfaceCLI, self.recevoirEnAttente)
        # recherche d'un player actif et si actif vrai . actif = isplaying
        # fill the menu Select a player


        self.actif , index_dictionnairedesPlayers ,  self.playerid = self.Players.playerActif(self.dictionnairedesplayers)

        # todo test
        #assert isinstance(index_dictionnairedesPlayers, object)
        #self.lePlayerActif = playerid[index_dictionnairedesPlayers]

        xbmc.log(str(self.actif) + '  ' + self.playerid, xbmc.LOGDEBUG)

        if self.actif:
            nombredeplayers = self.dictionnairedesplayers[0]['count']
            for x in range(1, nombredeplayers + 1):
                if (self.dictionnairedesplayers[x]['connected'] == '1'):
                    self.listMenu_Initialisation.addItem(self.dictionnairedesplayers[x]['name'])
            # todo : afficher dans une boite-liste les players et en évidence le player actif
            # or choose the player by user
            #
        else:
            line1 = " no player to listen to music , Exit program " + '\n' + \
                    " Error n° 36. Quit the programm , bye bye"
            xbmcgui.Dialog().ok('Players Problem', line1)
            self.quit()
            exit(36)
        # fin function initialisation serveur et players

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

        xbmc.log("soumission ArtWork : " + reponse, xbmc.LOGNOTICE)
        # find fonction set_artwork_size

    def update_now_is_playing(self):
        self.Window_is_playing = xbmcgui.getCurrentWindowId()
        #xbmc.log('fenetre de player en maj n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        #xbmc.log('nouvelle fenetre de player n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        # activation de la souscription au serveur process = Thread(target=crawl, args=[urls[ii], result, ii])
        self.subscribe = Souscription(self.InterfaceCLI , self.playerid,  self.Abonnement, self.recevoirEnAttente )
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
            timeoutduVolume = time.time() + 20
            while (self.breakBoucle_A == False):  # Boucle A principale de Subscribe

                if time.time() > timeoutdeTestdelaBoucle:
                    xbmc.log('Timeout : break A  ', xbmc.LOGNOTICE)
                    self.jivelette.bouton_pause.setVisible(False)
                    self.jivelette.bouton_play.setVisible(False)

                    break

                if time.time() > timeoutduVolume:
                    self.jivelette.label_volume.setVisible(False)
                    self.jivelette.slider_volume.setVisible(False)
                if not self.Abonnement.is_set:
                    break
                if xbmc.Monitor().waitForAbort(0.5):
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
                #xbmc.log('trame recue suite à suscribe : ' + str(pourLog), xbmc.LOGDEBUG)
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

                # Todo : analyse du bloc

                recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
                listeB = recupropre.split('subscribe:' + TIME_OF_LOOP_SUBSCRIBE +'|')  # on élimine le début de la trame # attention doit correpondre à
                # la même valeur de subscribe dans Ecoute.py
                try:
                    textC = listeB[1]  # on conserve la deuximème trame après suscribe...
                except IndexError:
                    break
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

                # xbmc.log(str(dico.viewitems()), xbmc.LOGDEBUG)
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
                    xbmc.log('percent duree : ' + str(pourcentagedureejouee) + ' - time: ' + dico['time'], xbmc.LOGDEBUG)
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

                try:
                    nouveautitre = dico['title']
                except KeyError:
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

                    self.InterfaceCLI.sendtoCLISomething('album ?')
                    reponse  = self.InterfaceCLI.receptionReponseEtDecodage()
                    album = reponse.split('album|').pop()
                    self.jivelette.labelAlbum.reset()
                    if not '|album' in album:
                        self.jivelette.labelAlbum.addLabel(label='[B]' + album + '[/B]')

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
                xbmc.log(str(compteur) + ' tour de boucle : ' + str(tempsparcouru), xbmc.LOGDEBUG)
                xbmc.log('bool jivelette.threadRunning : ' + str(self.jivelette.threadRunning), xbmc.LOGNOTICE)
                if not self.jivelette.threadRunning:
                    xbmc.log(' jivelette.threadRunning is not True ', xbmc.LOGNOTICE)
                    #self.subscribe.resiliersouscription() # double emploi
                    self.breakBoucle_A = True
                    self.Abonnement.clear()

                # effacer les boutons :


                # fin de la boucle A : sortie de subscribe
        # fin boucle while
        xbmc.log('End of Boucle of Squueze , Bye', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        # comment allons nous arrèter la souscription (dans le bouton stop ou exit du gui)
        # self.InterfaceCLIduLMS.demandedeStop.set()
        # on demande au Thread de s'arréter  par un flag
        #self.InterfaceCLI.closeconnexionWithCLI()
        time.sleep(0.2)
        #del  self.InterfaceCLI
        #self.demandedeStop.set()
        xbmc.log('End of fonction update_now_is_playing , Bye', xbmc.LOGNOTICE)
    #fin fonction update_now_is_playing

    def stop_now_is_playing(self):
        pass

    def update_random_mix_Playlist(self):

        xbmc.log(' entrée dans le random mix de la FramePlaylist', xbmc.LOGNOTICE)
        self.Window_is_playing = xbmcgui.getCurrentWindowId()
        #xbmc.log('fenetre de player en maj n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        #xbmc.log('nouvelle fenetre de player n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        # activation de la souscription au serveur process = Thread(target=crawl, args=[urls[ii], result, ii])
        self.subscribe = Souscription(self.InterfaceCLI , self.playerid,  self.Abonnement, self.recevoirEnAttente )
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
                xbmc.log('current_index_title :' + playlist_current_index_title, xbmc.LOGNOTICE)
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
                    xbmc.log('percent duree : ' + str(pourcentagedureejouee) + ' - time: ' + dico['time'],
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
                xbmc.log('playlist à traiter : ' + str(playlistatraiter), xbmc.LOGNOTICE)

                for champs in playlistatraiter:
                    xbmc.log('champs : ' + str(champs), xbmc.LOGNOTICE)

                    indexdeID = champs.find('|id:')
                    indexdeTitre = champs.find('|title:')
                    titre = champs[indexdeTitre + 7:]
                    track_id = champs[indexdeID + 4: indexdeTitre]
                    playlist_index = champs[0: indexdeID]
                    xbmc.log('index : ' + playlist_index, xbmc.LOGNOTICE)

                    if playlist_index == '0' :
                        xbmc.log('Titre : ' + titre + ' - Titre_index_O : ' + Titre_of_index_0 , xbmc.LOGNOTICE)
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
                xbmc.log(' jivelette.threadRunning is not True ', xbmc.LOGNOTICE)
                self.Abonnement.clear()

            if not old_current_index_title == playlist_current_index_title:
                self.frameRandomPlay.listMenu_playlist.selectItem(int(playlist_current_index_title))
                old_current_index_title = playlist_current_index_title

            self.InterfaceCLI.sendtoCLISomething('album ?')
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            album = reponse.split('album|').pop()
            #self.frameRandomPlay.labelAlbum.reset()
            self.frameRandomPlay.labelAlbum.setLabel(label='[B]' + album + '[/B]')

            self.InterfaceCLI.sendtoCLISomething('artist ?')
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            artist = reponse.split('artist|').pop()
            #self.frameRandomPlay.labelArtist.reset()
            self.frameRandomPlay.labelArtist.setLabel(label='[B]' + artist + '[/B]')

            self.InterfaceCLI.sendtoCLISomething('title ?')
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            artist = reponse.split('title|').pop()
            #self.frameRandomPlay.labelTitle.reset()
            self.frameRandomPlay.labelTitle.setLabel(label='[B]' + artist + '[/B]')

        # else:
        #     # here subscribe doesn't work
        #     self.functionNotYetImplemented()
        #     return
        xbmc.log('End of Boucle in Update random mix', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()

    # end random mix

 # fin fonction fillThePlaylist

    # racine -> branches -> feuilles -> fleurs ->  etamines
    # root ->   branchs ->  leaves - >  flowers -> stamens

    def les_menus_feuilles_Extras(self, numeroItemSelectionBranche):
        self.functionNotYetImplemented((self.listMenu_Feuilles))

    def get_artwork(self, index , artwork_track_id):
        '''
                fetch the image artwork  or icon from server or somewhere in tne net
                and store it in a temporay directory .

        '''
        filename = 'artwork.image_' + str(index) + '_' + str(artwork_track_id) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)
        xbmc.log('filename artwork : ' + str(completeNameofFile), xbmc.LOGNOTICE)
        # http://<server>:<port>/music/<track_id>/cover.jpg
        urltoopen = 'http://' + self.lmsip + ':' + self.lmswebport + '/music/' + artwork_track_id + '/cover.jpg'

        try:
            urllib.urlretrieve(urltoopen, completeNameofFile)
        except IOError:
            pass

        xbmc.log('nom du fichier image : ' + completeNameofFile, xbmc.LOGNOTICE)

        return completeNameofFile
        # fin fonction fin fonction get_icon, class Plugin_Generique
        # test


    def functionNotYetImplemented(self, menu):
        itemdeListe_1 = xbmcgui.ListItem()
        itemdeListe_1.setLabel('Not Yet')
        menu.addItem(itemdeListe_1)
        #itemdeListe_2 = xbmcgui.ListItem() # attention nouvelle référence sinon utiliser itemdeListe.copy()
        #itemdeListe_2.setLabel('Yet')
        #menu.addItem(itemdeListe_2)
        itemdeListe_3= xbmcgui.ListItem()
        itemdeListe_3.setLabel('Implemented')
        menu.addItem(itemdeListe_3)
        itemdeListe_4 = xbmcgui.ListItem()
        itemdeListe_4.setLabel('correctly')
        menu.addItem(itemdeListe_4)
        itemdeListe_5 = xbmcgui.ListItem()
        itemdeListe_5.setLabel('need more stuff')
        menu.addItem(itemdeListe_5)

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
            self.InterfaceCLI.sendtoCLISomething(requete)
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            del reponse

        else:

            requete = self.playerid + ' pause 0'
            self.InterfaceCLI.sendtoCLISomething(requete)
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            if 'pause' in reponse:
                self.bouton_pause.setVisible(False)
                self.flagStatePause = False
            del reponse

    @singleton
    def setVolume(self, UpOrDown):
        # need to know the actual volume in percent
        #self.get_playerid()
        #self.get_ident_server()
        #self.connectInterface()

        def onAction(self, action):
            if action == xbmcgui.ACTION_PREVIOUS_MENU:
                self.label_volume.setVisible(False)
                self.slider_volume.setVisible(False)

            elif action == ACTION_VOLUME_UP:    # it's the volume key Vol+  on my remote
                self.setVolume('UP')

            elif action == ACTION_VOLUME_DOWN:  # it's the volume key Vol-  on my remote
                self.setVolume('DOWN')
            
        
        requete = self.playerid + ' mixer volume ?'
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        temp = reponse.split('volume|')
        volumePercent = float(temp[1])
        self.slider_volume.setPercent(volumePercent)
        self.label_volume.setLabel('Volume on ' + self.playerid + ' - - -  ' + str(volumePercent) + ' %')

        self.label_volume.setVisible(True)
        self.slider_volume.setVisible(True)

        if UpOrDown == 'UP':
            volumePercent = volumePercent + 5.
            if volumePercent >= 100:
                volumePercent = 100

        elif UpOrDown == 'DOWN':
            volumePercent = volumePercent - 5.
            if volumePercent < 0 :
                volumePercent = 0
        else:
            pass
        requete = self.playerid + ' mixer volume ' + str(volumePercent)
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        self.slider_volume.setPercent(volumePercent)
        
            

