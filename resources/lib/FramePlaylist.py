#!/usr/bin/env python
# -*- coding: utf-8 -*-

global savepath
#savepath = '/tmp/' # savepath = 'special://temp'


global Kodi
Kodi = True

#sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))

import threading
import time
import urllib
import os

from resources.lib import ConnexionClient, Ecoute, outils
from resources.lib.Ecoute import Souscription
from resources.lib import pyxbmctExtended


import json

if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct


    SIZE_WIDTH_pyxbmct = 1280
    SIZE_HEIGHT_pyxbmct = 720
    SEIZE = 16 * 4  #32 16 option in a  16:9 screen here it's  64:36 squares
    NEUF =   9 * 4  #18 or 9

    ADDON = xbmcaddon.Addon()
    ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))
    savepath = xbmc.translatePath('special://temp')

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


    ACTION_PAUSE = 12
    ACTION_PLAY = 68
    ACTION_PLAYER_PLAY = 79

    ACTION_VOLAMP_DOWN = 94
    ACTION_VOLAMP_UP = 93
    ACTION_VOLUME_DOWN = 89
    ACTION_VOLUME_UP = 88

    TIME_OF_LOOP_SUBSCRIBE = Ecoute.TIME_OF_LOOP_SUBSCRIBE

TAGS = 'aCdejJKlstuwxy'

def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

#@singleton
class PlaylistPlugin(pyxbmctExtended.BackgroundDialogWindow):

    def __init__(self, *args , **kwargs ):
        #title = args[0]
        super(PlaylistPlugin, self).__init__()

        self.recevoirEnAttente = threading.Event()
        self.recevoirEnAttente.clear()
        self.Abonnement = threading.Event()
        self.threadRunning = True
        self.WindowPlaying = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre de class PlaylistPlugin n° : ' + str(self.WindowPlaying), xbmc.LOGNOTICE)
        xbmc.log('Create Instance PlaylistPlugin KodiJivelette...' , xbmc.LOGNOTICE)
        self.playerid = ''
        self.geometrie()
        xbmc.log('geometrie set', xbmc.LOGNOTICE)
        self.controlMenus()
        xbmc.log('control set', xbmc.LOGNOTICE)
        xbmc.log('navigation  set', xbmc.LOGNOTICE)

        self.connexionEvent()
        self.connect(self.listMenu_playlist, self.selectActionofItem)
        self.set_navigation()


        # initialisation diverses :
        self.connectInterface()
        self.get_ident_server()
        self.get_playerid()

        time.sleep(0.5)

        #self.affichequelquesInfos()

        #self.randomPlaylist()


    def geometrie(self):
        SIZESCREEN_HEIGHT = xbmcgui.getScreenHeight()            # exemple  # 1080
        SIZESCREEN_WIDTH = xbmcgui.getScreenWidth()                         # 1920

        # replaced by pyxbmct but need for the size cover until the fix
        self.GRIDSCREEN_Y, Reste = divmod(SIZESCREEN_HEIGHT, 10)            # 108
        self.GRIDSCREEN_X, Reste = divmod(SIZESCREEN_WIDTH, 10)             # 192

        self.screenx = SIZESCREEN_WIDTH
        self.screeny = SIZESCREEN_HEIGHT
        xbmc.log('Real Size of Screen : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        if self.screenx > SIZE_WIDTH_pyxbmct:
            self.screenx = SIZE_WIDTH_pyxbmct  # try
            self.screeny = SIZE_HEIGHT_pyxbmct

        self.image_dir = ARTWORK  # path to pictures used in the program (future development, todo)

        self.cover_jpg = self.image_dir + '/music.png'  # pour le démarrage then updated
        self.image_background = self.image_dir + '/fond-noir.jpg'  # in next release could be change by users
        self.image_progress = self.image_dir + '/ajax-loader-bar.gif'  # not yet used, get from speedtest
        #self.image_button_pause = self.image_dir + '/pause.png'  # get from Xsqueeze
        #self.image_button_stop = self.image_dir + '/stop.png'  # get from Xsqueeze not used
        #self.image_button_play = self.image_dir + '/play.png'  # get from Xsqueeze
        self.image_button_play = self.image_dir + '/icon_toolbar_play.png'  # get from jivelite
        self.image_button_pause = self.image_dir + 'icon_toolbar_pause.png'     # get from jivelite

        self.textureback_slider_duration = self.image_dir + '/slider_back.png'  # get from plugin audio spotify
        self.texture_slider_duration = self.image_dir + '/slider_button_new.png'
        self.image_list_focus = self.image_dir + '/MenuItemFO.png'  # myself

        #pyxbmct :
        self.setGeometry(self.screenx  , self.screeny , NEUF, SEIZE)
        xbmc.log('Size of Screen pyxbmct fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)
        # cover when playing
        SIZECOVER_X = (SEIZE // 2) - 6  #  int(self.screenx / SEIZE * 28 )
        self.sizecover_x = SIZECOVER_X
        #SIZECOVER_Y = self.GRIDSCREEN_Y * 3  # and reserve a sized frame to covers,attention SIZECOVER_X != SIZECOVER_Y
        xbmc.log('Taille pochette : ' + str(SIZECOVER_X) + ' x ' + str(SIZECOVER_X) , xbmc.LOGNOTICE)

        ligneButton = NEUF - 3
        SLIDER_INIT_VALUE = 0
        # reserve pour afficher cover.jpg
        self.image_dir = ARTWORK    # path to pictures used in the program

        self.cover_jpg = self.image_dir + '/vinyl.png'      # pour le démarrage then updated
        # reserve pour afficher cover.jpg
        self.pochette = pyxbmct.Image(self.cover_jpg)
        self.placeControl(control=self.pochette,
                          row=1,
                          column=(SEIZE // 2) - 2,
                          rowspan=28,
                          columnspan=29)  # todo to fix
        self.pochette.setImage(self.cover_jpg)

        # Slider de la durée
        self.slider_duration = pyxbmct.Slider(textureback=self.textureback_slider_duration)
        self.placeControl(control= self.slider_duration,
                          row= ligneButton - 4 ,
                          column= ( SEIZE // 2 ) + 2   ,
                          rowspan=1 ,
                          columnspan= 21 ,
                          pad_x = 5 ,
                          pad_y = 5 )
        self.slider_duration.setPercent(SLIDER_INIT_VALUE)

        # labels des durée
        self.labelduree_jouee = pyxbmct.Label('')
        self.placeControl(control=self.labelduree_jouee,
                          row=ligneButton - 4 ,
                          column=( SEIZE // 2 ) - 2,
                          rowspan= 2 ,
                          columnspan = 5 ,
                          pad_x = 5 ,
                          pad_y = 5 )
        self.labelduree_fin = pyxbmct.Label('')
        self.placeControl(control=self.labelduree_fin,
                          row= ligneButton - 4 ,
                          column=( SEIZE // 2 ) + 23 ,
                          rowspan=2 ,
                          columnspan= 3 ,
                          pad_x = 5 ,
                          pad_y = 5 )

        self.labelAlbum = pyxbmct.Label(label='' ,
                                        font='font13',
                                        textColor='0xFF888888',
                                        alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.labelAlbum,
                          row=ligneButton - 2 ,
                          column= ( SEIZE // 2 ) ,
                          rowspan= 1,
                          columnspan=27 )
        self.labelAlbum.setLabel('Album')

        self.labelArtist = pyxbmct.Label(label='' ,
                                         font='font13',
                                         textColor='0xFF888888',
                                         alignment=pyxbmct.ALIGN_CENTER )
        self.placeControl(self.labelArtist,
                          row=ligneButton - 1 ,
                          column= ( SEIZE // 2 ) ,
                          rowspan= 1,
                          columnspan=27 )
        self.labelArtist.setLabel('Artist')

        self.labelTitle = pyxbmct.Label(label='' ,
                                        font='font13',
                                        textColor='0xFF888888',
                                        alignment=pyxbmct.ALIGN_CENTER )
        self.placeControl(self.labelTitle,
                          row=ligneButton - 0 ,
                          column= SEIZE // 2  ,
                          rowspan= 1,
                          columnspan=27 )
        self.labelTitle.setLabel('Title')

    def controlMenus(self):
        ''' Fix the size of itemlists in menus lists'''

        self.title_label = pyxbmct.Label('Random Play', textColor='0xFF808080')
        self.placeControl(self.title_label, 0 , 2 , 1 , 10)

        row_depart = 2
        col_depart = 0
        espace_row = 35
        espace_col = SEIZE / 4
        hauteur_menu = 25

        self.listMenu_playlist = pyxbmct.List(buttonFocusTexture=self.image_list_focus,
                                              _imageWidth= 40 ,
                                              _imageHeight = 40 ,
                                              _itemHeight= 42 )

        self.placeControl(self.listMenu_playlist , row_depart , col_depart  , espace_row, (SEIZE / 2) - 2 )

        # TRES IMPORTANT POUR AVOIR LE FOCUS
        # Add items to the list , need to ask the focus before filling the list from Plugin.Plugin
        self.listMenu_playlist.addItem('')
        self.listMenu_playlist.setEnabled(True)


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

    #def onControl(self, control):
    #    print("Window.onControl(control=[%s])" % control)

    def onAction(self, action):
        """
        Catch button actions.

        ``action`` is an instance of :class:`xbmcgui.Action` class.
        """
        if action == ACTION_PREVIOUS_MENU:
            xbmc.log('Previous_menu' + str(action), xbmc.LOGNOTICE)
            self.quit_listing()

        elif action == ACTION_NAV_BACK:
            xbmc.log('nav_back', xbmc.LOGNOTICE)
            self.quit_listing()

        elif action == ACTION_PAUSE:  # currently it's the space on my keyboard
            xbmc.log('Action Pause', xbmc.LOGNOTICE)
            self.pause_play()

        elif action == ACTION_PLAY or action == ACTION_PLAYER_PLAY:
            xbmc.log('Action Play', xbmc.LOGNOTICE)
            self.pause_play()

        elif action == ACTION_VOLUME_UP:  # it's the volume key Vol+  on my remote
            xbmc.log('Action Volume' +  str(action), xbmc.LOGNOTICE)
            self.promptVolume()

        elif action == ACTION_VOLUME_DOWN:  # it's the volume key Vol-  on my remote
            xbmc.log('Action Volume', xbmc.LOGNOTICE)
            self.promptVolume()

        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            xbmc.log('Action context Menu', xbmc.LOGNOTICE)
            self.promptContextMenu()

        else:
            xbmc.log('else condition onAction in FramePlaylist', xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)

    def quit_listing(self):# todo : à tester
        self.WindowPlayinghere = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre PlaylistPlugin  is exiting: ' + str(self.WindowPlayinghere), xbmc.LOGNOTICE)

        self.connectInterface()
        self.get_playerid()
        self.subscribe = Ecoute.Souscription(self.InterfaceCLI, self.playerid )
        self.subscribe.resiliersouscription()
        xbmc.log('send resiliersouscription in A quit() FramePlaylist', xbmc.LOGNOTICE)
        self.threadRunning = False
        self.close()

    def pause_play(self):
        self.get_playerid()
        self.get_ident_server()
        self.connectInterface()

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

    def futureFunction(self):
        pass

    def set_navigation(self):

        # Set navigation between controls (Button, list or slider)
        # Control has to be added to a window first if not raise RuntimeError
        # Set initial focus , don't forget to fill an item before setfocus
        self.setFocus(self.listMenu_playlist)
        
    def list_Menu_Navigation(self):
        # todo écrire quoi faire quand on bouge les flèches , la souris
        # à priori on veut juste naviguer entre les élements
        # ou bien selectionner l'action sur le menu
        # ce qui est fait par le connect
        if self.getFocus() == self.listMenu_playlist:
            self.itemSelection = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getLabel()
            self.title_label.setLabel(self.itemSelection)

    def randomPlaylist(self): # not used , Todo  Delete it or change logic

        xbmc.log(' entrée dans le random mix de la FramePlaylist', xbmc.LOGNOTICE)

        self.connectInterface()
        self.get_ident_server()
        self.get_playerid()

        listenrequete = self.playerid + ' status 0 100 subscribe:' + TIME_OF_LOOP_SUBSCRIBE
        self.InterfaceCLI.sendtoCLISomething(listenrequete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()

        if 'subscribe:' in reponse:

            self.setFocus(self.listMenu_playlist)
            self.listMenu_playlist.reset()
            self.listMenu_playlist.setVisible(True)

            compteur = 0
            self.update_coverbox(lmsip=self.lmsip, lmswebport=self.lmswebport, playerid=self.playerid,
                                                 compteur=compteur)
            # reponse = self.InterfaceCLI.receptionReponseEtDecodageavecCR()

            while self.Abonnement.is_set():

                if self.mustQuit:
                    self.quit_listing()
                    break
                # while reponse:
                # if xbmc.Monitor().waitForAbort(1):
                #    break

                compteur = compteur + 1
                self.update_coverbox(lmsip=self.lmsip, lmswebport=self.lmswebport,
                                                     playerid=self.playerid, compteur=compteur)

                poubelle, atraiter = reponse.split('subscribe:' + TIME_OF_LOOP_SUBSCRIBE + '|')
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
                # xbmc.log('index debut : ' + str(indexdecurrentTitle) + ' fin : ' + str(indexFincurrentTitle), xbmc.LOGDEBUG)
                playlist_current_title = atraiter[indexdecurrentTitle + 10: indexFincurrentTitle]

                listedechamps = atraiter.split('|playlist index:')
                playlistatraiter = listedechamps[1:]
                xbmc.log('playlist à traiter : ' + str(playlistatraiter), xbmc.LOGNOTICE)

                for champs in playlistatraiter:
                    xbmc.log('champs : ' + str(champs), xbmc.LOGNOTICE)

                    indexdeID = champs.find('|id:')
                    indexdeTitre = champs.find('|title:')
                    # xbmc.log('index ID : ' + str(indexdeID) + ' titre : ' + str(indexdeTitre), xbmc.LOGDEBUG)

                    titre = champs[indexdeTitre + 7:]
                    # xbmc.log('titre : ' + titre , xbmc.LOGDEBUG)
                    track_id = champs[indexdeID + 4: indexdeTitre]
                    # xbmc.log('track_id : ' + str(track_id) , xbmc.LOGDEBUG)
                    playlist_index = champs[0: indexdeID]
                    tracktampon = xbmcgui.ListItem()
                    tracktampon.setLabel(titre)
                    tracktampon.setProperty('track_id', track_id)
                    tracktampon.setProperty('index', playlist_index)
                    try:
                        dejaexistant = self.listMenu_playlist.getListItem(int(playlist_index))
                    except RuntimeError:
                        # dont exist so add it
                        self.listMenu_playlist.addItem(tracktampon)

                self.listMenu_playlist.selectItem(int(playlist_current_title))
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()

        else:
            # here subscribe doesn't work
            self.functionNotYetImplemented()
            return

        listenrequete = self.playerid + ' status 0 100 subscribe:-'
        self.InterfaceCLI.sendtoCLISomething(listenrequete)
        reponselisten = self.InterfaceCLI.receptionReponseEtDecodage()

     # fin fonction fillThePlaylist

    def selectActionofItem(self):

        dialogWhattoDo = xbmcgui.Dialog().select(heading='What To Do ?' , \
                                                 list= ['Play this track', 'Info about this track'])
        if dialogWhattoDo == -1:
            return
        elif dialogWhattoDo == 0:
            self.jumpPlaytoThisItem()
        elif dialogWhattoDo == 1:
            self.detailItemPlaylist()
        else:
            return

    def jumpPlaytoThisItem(self):
        labelajouer = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getLabel()
        xbmc.log('label info :' + labelajouer , xbmc.LOGNOTICE)
        track_id = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getProperty('track_id')
        xbmc.log('track_id info :' + track_id , xbmc.LOGNOTICE)
        playlist_index = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getProperty('index')

        # requete = self.playerid + ' playlist index ?'
        # self.InterfaceCLI.sendtoCLISomething(requete)
        # reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        # current_index = reponse.split('index|').pop()
        # intsaut = int(current_index) - int(playlist_index)
        # saut = str(intsaut)
        # jump to this track and play it
        requete = self.playerid + ' playlist index ' + playlist_index
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()

    def detailItemPlaylist(self):

        labelajouer = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getLabel()
        xbmc.log('label info :' + labelajouer , xbmc.LOGNOTICE)
        track_id = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getProperty('track_id')
        xbmc.log('track_id info :' + track_id , xbmc.LOGNOTICE)

        requete = self.playerid + ' songinfo 0 100 track_id:' + str(track_id)
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        try:
            listesonginfo = reponse.split('|')
        except ValueError:
            self.functionNotYetImplemented()
            return

        textInfo = ''
        for field in listesonginfo:
            textInfo = textInfo +  field + '\r\n'

        dialogSongInfo = xbmcgui.Dialog()
        dialogSongInfo.textviewer('Song Info : ' + labelajouer , textInfo )

    def affichequelquesInfos(self):
        labelajouer = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getLabel()
        xbmc.log('label info :' + labelajouer , xbmc.LOGNOTICE)
        track_id = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getProperty('track_id')
        xbmc.log('track_id info :' + track_id , xbmc.LOGNOTICE)
        requete = self.playerid + ' songinfo 0 100 track_id:' + str(track_id)
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        try:
            listesonginfo = reponse.split('|')
            xbmc.log('songinfo : ' + str(listesonginfo), xbmc.LOGNOTICE)
        except ValueError:
            self.functionNotYetImplemented()
            return

    def functionNotYetImplemented(self):
        '''
        print in a menu (n°4) of the screen
        perhaps it could rather alert in  a dialogbox ? (todo)
        :return:
        '''

        self.title_label.setLabel('Nobody is perfect')

        itemdeListe_1 = xbmcgui.ListItem()
        itemdeListe_1.setLabel('function Not Yet')
        self.listMenu_4.addItem(itemdeListe_1)

        itemdeListe_2= xbmcgui.ListItem()
        itemdeListe_2.setLabel('Implemented')
        self.listMenu_4.addItem(itemdeListe_2)

        itemdeListe_3 = xbmcgui.ListItem()
        itemdeListe_3.setLabel('correctly')
        self.listMenu_4.addItem(itemdeListe_3)

        itemdeListe_4 = xbmcgui.ListItem()
        itemdeListe_4.setLabel('need more stuff')
        self.listMenu_4.addItem(itemdeListe_4)

        # fin fonction fin fonction functionNotYetImplemented, class Plugin_Generique

    # copier/coller de la fonction de FrameMenu.py
    def update_current_track_playing(self): # not yet used , Todo : Delete it or change logic

        self.subscribe = Souscription(self.InterfaceCLI, self.playerid )
        self.subscribe.subscriptionLongue()
        # todo Q : comment faire la gestion de l'arret de la boucle de souscription ?
        #      A : fonction resiliersouscription()

        time.sleep(0.5)

        timeoutdeTestdelaBoucle = time.time() + 60 * 10  # 10 minutes from now -for testing
        timeoutdeRecherchedesPlayers = time.time() + 60 * 20  # todo toutes les 20 minutes nous rechercherons les players
        timeEntreeDansLaBoucle = time.time()
        compteur = 1
        titreenlecture = ''
        self.breakBoucle_A = False
        while (self.breakBoucle_A == False):  # Boucle A principale de Subscribe

            if time.time() > timeoutdeTestdelaBoucle:
                xbmc.log('Timeout : break A  ', xbmc.LOGNOTICE)
                break

            if xbmc.Monitor().waitForAbort(0.5):
                self.breakBoucle_A = True

            # Todo : analyse du bloc

            recupropre = self.InterfaceCLI.receptionReponseEtDecodage()

            if 'subscribe:-' in recupropre:  # fin souscription the resiliersouscription is send by FramePlaying or
                                             # else diplaying
                                             # the FramePlaying  exits - function quit()
                self.breakBoucle_A = True    # must exit the loop A
                #self.Abonnement.clear()      # must exit the main loop
                break

            listeB = recupropre.split('subscribe:' + TIME_OF_LOOP_SUBSCRIBE + '|')  # on élimine le début de la trame
            # attention doit correpondre à
            # la même valeur de subscribe dans Ecoute.py
            try:
                textC = listeB[1]  # on conserve la deuximème trame après suscribe...
            except IndexError:
                break
                # pass
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

            try:
                pourcentagedureejouee = 100 * float(dico['time']) / float(dico['duration'])
                xbmc.log('percent duree : ' + str(pourcentagedureejouee) + ' - time: ' + dico['time'],
                         xbmc.LOGDEBUG)
            except KeyError:
                pourcentagedureejouee = 0

            try:
                self.slider_duration.setPercent(pourcentagedureejouee)
                # self.slider_duration.setPercent(pourcentagedureejouee)
            except KeyError:
                pass

            try:
                self.labelduree_jouee.setLabel(label=outils.getInHMS(dico['time']))
                # self.labelduree_jouee.setLabel(label= outils.getInHMS(self, dico['time']))
            except KeyError:
                pass

            try:
                self.labelduree_fin.setLabel(label=outils.getInHMS(dico['duration']))
                # self.labelduree_fin.setLabel(label= outils.getInHMS(self, dico['duration']))
            except KeyError:
                self.labelduree_fin.setLabel(label=outils.getInHMS(0.0))

            if not dico['title'] == titreenlecture:

                try:
                    self.title_label.setLabel(label='[B]' + dico['current_title'] + '[/B]')
                except KeyError:
                    self.title_label.setLabel(label='')
                    pass

                #self.update_coverbox(self.lmsip, self.lmswebport, self.playerid, compteur)

            # log pour voir
            compteur += 1
            timedutour = time.time()
            tempsparcouru = timedutour - timeEntreeDansLaBoucle
            xbmc.log(str(compteur) + ' tour de boucle : ' + str(tempsparcouru), xbmc.LOGDEBUG)
            #xbmc.log('bool jivelette.threadRunning : ' + str(self.jivelette.threadRunning), xbmc.LOGNOTICE)
            if pourcentagedureejouee >= 100:
                self.breakBoucle_A = True
                break

                # fin de la boucle A : sortie de subscribe
        # fin boucle while
        xbmc.log('End of Boucle of update_current_track_playing in FramePlaylist , Bye', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        #self.InterfaceCLI.viderLeBuffer()
        xbmc.log('End of fonction update_current_track_playing in FramePlaylist , Bye', xbmc.LOGNOTICE)
    # fin fonction update_current_track_playing

    def connectInterface(self):
        self.InterfaceCLI = ConnexionClient.InterfaceCLIduLMS()

    def get_playerid(self):
        self.Players = outils.WhatAreThePlayers()
        #self.playerid = self.Players.get_unplayeractif()
        self.playerid = self.Players.playerSelectionID

    def get_ident_server(self):
        self.Server = outils.WhereIsTheLMSServer()
        self.nomserver = self.Server.LMSnom
        self.lmsip = self.Server.LMSCLIip
        self.lmswebport = self.Server.LMSwebport

    def get_icon(self, index, urlicone):
        '''
        fetch the image or icon from server or somewhere in tne net
        and store it in a temporay directory .
        ie /tmp/ on unix or
        special://tmp doesn't seems work on librelec
        '''
        filename = 'icon.image_' + str(index) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)
        xbmc.log('filename icon : ' + str(completeNameofFile), xbmc.LOGDEBUG)

        if 'http' in urlicone:
            urltoopen = urlicone
        else:
            if urlicone.startswith('/'):
                xbmc.log('url icone avec /: ' + urlicone ,xbmc.LOGDEBUG )
            #urltoopen = 'http://' + self.origine.rechercheduserveur.LMSCLIip + ':' + self.origine.rechercheduserveur.LMSwebport + '/' + urlicone
                urltoopen = 'http://' + self.lmsip + ':' + self.lmswebport + urlicone
            else:
                xbmc.log('url icone sans /: ' + urlicone ,xbmc.LOGDEBUG )
                urltoopen = 'http://' + self.lmsip + ':' + self.lmswebport + '/' + urlicone
        try:
            urllib.urlretrieve(urltoopen, completeNameofFile)
        except IOError:
            self.functionNotYetImplemented()
        xbmc.log('nom du fichier image : ' + completeNameofFile , xbmc.LOGNOTICE)
        return completeNameofFile
        # fin fonction fin fonction get_icon, class Plugin_Generique
        # test

    def get_artwork(self, hashcode_artwork):
        #http://<server>:<port>/music/<track_id>/cover.jpg
        filename = 'icon.image_' + str(hashcode_artwork) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)
        
        urlimage = 'http://' + self.lmsip + ':' + self.lmswebport + '/music/' + str(hashcode_artwork) + '/cover.jpg'
        
        try:
            urllib.urlretrieve(urlimage, completeNameofFile)
        except IOError:
            pass
            self.functionNotYetImplemented()
        
        xbmc.log('nom du fichier image : ' + completeNameofFile , xbmc.LOGNOTICE)
        return completeNameofFile

    def update_coverbox(self, lmsip, lmswebport, playerid, compteur):
            '''
            fonction qui devrait mettre à jour l'affichage de la pochette
            dans cette version on récupère la pochette du serveur pour le player courant
            dans une autre version on récupère la pochette du serveur grâce au tag fourni
            dans l'information sur la chanson en cours

            Same function in FramePlaying.py (redondance)
            :param lmsip:
            :param lmswebport:
            :param playerid:
            :return:
            '''
            # on construit l'url de récupération de l'image
            #http://<server>:<port>/music/current/cover.jpg?player=<playerid>
            # exemple : http://192.168.1.101:9000/music/current/cover.jpg?player=00:04:20:17:1c:44
            # ou bien http://<server>:<port>/music/<track_id>/cover.jpg
            # exemple :
            urlcover = 'http://' + lmsip + ':' + lmswebport + \
                       '/music/current/cover.jpg?player=' + playerid    # or self.playerID ?
            xbmc.log(urlcover, xbmc.LOGNOTICE)
            filename = 'pochette' + str(compteur) + '.tmp'
            completeNameofFile = os.path.join(savepath , filename )
            xbmc.log('filename tmp : ' + str(completeNameofFile), xbmc.LOGNOTICE)
            urllib.urlretrieve(urlcover , completeNameofFile)
            self.pochette.setImage(completeNameofFile) # fonction d'xbmcgui
            #os.remove(completeNameofFile)  # suppression du fichier
            # fin fonction update_cover

    def futureFunction(self):
        pass

    def promptVolume(self):
        volumeFrame = outils.VolumeFrameChild()
        volumeFrame.doModal()
        del volumeFrame

    def promptContextMenu(self):
        contextMenuFrame = outils.ContextMenuFrameChild()
        contextMenuFrame.doModal()
        del contextMenuFrame
