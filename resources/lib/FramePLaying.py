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
import urllib
import random
import threading
import time

from resources.lib import ConnexionClient
from resources.lib import outils, Ecoute
from resources.lib import pyxbmctExtended
from resources.lib.outils import debug

TIME_OF_LOOP_SUBSCRIBE = Ecoute.TIME_OF_LOOP_SUBSCRIBE

sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))

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
    global savepath
    savepath = xbmc.translatePath('special://temp')


    # screen 16:9 so to have grid square fix to 16-9 on 1280 x 720 max of pyxbmct
    SIZE_WIDTH_pyxbmct = 1280
    SIZE_HEIGHT_pyxbmct = 720
    SEIZE = 16 * 4  #32 16 option -> 64
    NEUF =   9 * 4  #18 or 9 -> 36
    # pgcd (720,1280) = 80
    # so if the grid is composed with square tiles , tiles must be 80 x 80 pixels
    # and SEIZE = 16 , NEUF = 9
    # 16 x 80 = 1280
    # 9 x 80 = 720
    # but  80 pixel is too large for 1 rowspan
    # with 16 x 4 and 9 x 4 we get tiles :
    # with 1920 pixels / 64 -> 30 px  x_tile
    # with 1080 pixels / 36 -> 30 px  y_tile
    # with 1280 px /64 -> 20px
    # with 720 px / 36 -> 20px
    # for a cover of 560 x 560 px we need 560 / 30 = 18,6666 not good
    # but 540 or 570 px is ok

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

tempsdeLecture = 1.0        # when a time.sleep(tempsdeLecture) is done to let the user read the screen. to ajust
                            # to be ergonomic or ask the user the wish timeout
def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper


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
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','fond-noir.jpg'))
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_vibrato.png'))


pyxbmct.addonwindow.skin = MySkin()


class SlimIsPlaying(pyxbmctExtended.BackgroundDialogWindow):
    '''
    Frame d'affichage de NowIsPlaying
        basé sur une extension de pyxbmct
        permet d'avoir un background
        pas de header ni title-bar ni titre
    '''
    # Or class SlimIsPlaying(pyxbmct.AddonFullWindow):

    def __init__(self, *args ):
        #title = args[0] # for AddonFullWindow
        #super(SlimIsPlaying, self).__init__( title)

        super(SlimIsPlaying, self).__init__()

        self.WindowPlaying = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre de class SlimIsPlaying n° : ' + str(self.WindowPlaying), xbmc.LOGNOTICE)
        xbmc.log('Create Instance Slim is Now Playing KodiJivelette...' , xbmc.LOGNOTICE)

        self.NowIsPlaying = True    # this is a flag for the main Loop in the method update
        self.threadRunning = True
        self.flagStatePause = False
        # initial setup to have self.InterfaceCli when update_now_is_playing() run inside this class :
        self.get_playerid()
        self.connectInterface()
        self.get_ident_server()

        debug('server : ' + self.nomserver + ' - ' + self.lmsip + ' : ' + self.lmswebport, xbmc.LOGNOTICE)
        debug('player : ' + self.playerid, xbmc.LOGNOTICE)

        SIZESCREEN_HEIGHT = xbmcgui.getScreenHeight()            # exemple  # 1080
        SIZESCREEN_WIDTH = xbmcgui.getScreenWidth()                         # 1920
        # Replaced by pyxbmct but need for the size cover until the fix
        self.GRIDSCREEN_Y, Reste = divmod(SIZESCREEN_HEIGHT, 10)            # 108
        self.GRIDSCREEN_X, Reste = divmod(SIZESCREEN_WIDTH, 10)             # 192

        self.screenx = SIZESCREEN_WIDTH
        self.screeny = SIZESCREEN_HEIGHT
        xbmc.log('Real Size of Screen : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        if self.screenx > SIZE_WIDTH_pyxbmct:
            self.screenx = SIZE_WIDTH_pyxbmct
            self.screeny = SIZE_HEIGHT_pyxbmct

        #pyxbmct :
        self.setGeometry(width_= self.screenx ,
                         height_=self.screeny ,
                         rows_= NEUF,
                         columns_= SEIZE)
        xbmc.log('Size of Screen pyxbmct fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        # sizecover must be  a square
        #SIZECOVER_X  = int(self.GRIDSCREEN_X * 2.5)  # need to ask artWork size from server, adapt to the size screen
        SIZECOVER_X = (SEIZE // 2) - 6  # int(self.screenx / SEIZE * 28 )
        self.sizecover_x = SIZECOVER_X
        #SIZECOVER_Y = self.GRIDSCREEN_Y * 3  # and reserve a sized frame to covers,attention SIZECOVER_X != SIZECOVER_Y
        xbmc.log('Taille pochette : ' + str(SIZECOVER_X) + ' x ' + str(SIZECOVER_X) , xbmc.LOGNOTICE)

        ligneButton = NEUF - 3
        SLIDER_INIT_VALUE = 0

        self.image_dir = ARTWORK    # path to pictures used in the program

        self.cover_jpg = self.image_dir + '/music.png'      # pour le démarrage then updated
        self.image_background = self.image_dir + '/fond-noir.jpg'  # in next release could be change by users
        self.image_progress = self.image_dir + '/ajax-loader-bar.gif'   # not yet used, get from speedtest
        #self.image_button_pause = self.image_dir + '/pause.png'   # get from Xsqueeze
        # self.image_button_stop = self.image_dir + '/stop.png'     # get from Xsqueeze
        self.image_button_play = self.image_dir + '/play.png'     # get from Xsqueeze
        #self.image_button_play = self.image_dir + '/icon_toolbar_play.png'  # get from jivelite
        self.image_button_pause = self.image_dir + '/icon_toolbar_pause.png'     # get from jivelite

        self.textureback_slider_duration = self.image_dir + '/slider_back.png'  # get from plugin audio spotify
        #self.textureback_slider_duration = self.image_dir + '/seekslider2.png'  # get from plugin Xsqueeze

        self.texture_slider_duration = self.image_dir + '/slider_button_new.png'

        self.image_list_focus = self.image_dir + '/MenuItemFO.png'  # myself

        # reserve pour afficher cover.jpg
        self.pochette = pyxbmct.Image(self.cover_jpg)
        self.placeControl(control=self.pochette,
                          row= 3 ,
                          column= ( SEIZE // 2 ) - 2 ,
                          rowspan= 28 ,
                          columnspan= 29 )  # todo to fix
        self.pochette.setImage(self.cover_jpg)

        # title of radio , apps songs ...
        self.labeltitre_1 = pyxbmct.FadeLabel( font= 'font50caps_title' , textColor ='0xFF888888' )
        self.placeControl(self.labeltitre_1,  8 , 4 , 3 , 25 )
        self.labeltitre_1.addLabel('')

        self.labeltitre_2 = pyxbmct.FadeLabel( font = 'font13', textColor ='0xFF888888' )
        self.placeControl(self.labeltitre_2, 12 , 4 , 2 , 25 )
        self.labeltitre_1.addLabel('')

        self.labelAlbum = pyxbmct.FadeLabel( font = 'font13', textColor ='0xFF888888' )
        self.placeControl(self.labelAlbum, 14 , 4 , 2 , 25 )
        self.labelAlbum.addLabel('')

        self.labelArtist = pyxbmct.FadeLabel( font = 'font13', textColor ='0xFF888888' )
        self.placeControl(self.labelArtist, 16 , 4 , 2 , 25 )
        self.labelArtist.addLabel('')

        # Slider de la durée
        self.slider_duration = pyxbmct.Slider(textureback=self.textureback_slider_duration)
        self.placeControl(control=self.slider_duration,
                          row= ligneButton - 2 ,
                          column= ( SEIZE // 2 )  ,
                          rowspan= 1 ,
                          columnspan= 29 - 4 ,
                          pad_x= 1)

        self.slider_duration.setPercent(SLIDER_INIT_VALUE)

        # labels des durée
        self.labelduree_jouee = pyxbmct.Label('')
        self.placeControl(control=self.labelduree_jouee,
                          row=ligneButton - 2 ,
                          column= ( SEIZE // 2 ) - 2 ,
                          rowspan= 2 ,
                          columnspan = 5 ,
                          pad_x = 5 ,
                          pad_y = 5 )
        self.labelduree_fin = pyxbmct.Label('')
        self.placeControl(control=self.labelduree_fin,
                          row= ligneButton - 2 ,
                          column= ( SEIZE // 2 ) - 2  + ( 29 - 3 ) ,
                          rowspan=2 ,
                          columnspan= 4 ,
                          pad_x = 5 ,
                          pad_y = 5 )



        # button pause : (Todo : rather a button maybe can do a frame Pause with the Button pause/play inside the frame)
        self.bouton_pause = pyxbmct.Button(label='', focusTexture=self.image_button_pause, noFocusTexture=self.image_button_pause)
        self.placeControl(control=self.bouton_pause,
                          row = ( NEUF // 2 ) - 5  ,
                          column= (SEIZE // 2) - 5  ,
                          rowspan= 10 ,
                          columnspan= 10 )
        self.bouton_pause.setVisible(False)
        self.bouton_play = pyxbmct.Button(label='', focusTexture=self.image_button_play, noFocusTexture='')
        self.placeControl(self.bouton_play , row = NEUF / 2 , column= (SEIZE / 2 ) - 2  , rowspan= 6 , columnspan= 6 )
        self.bouton_play.setVisible(False)

        #  connect key
        # zone de contrôle des actions
        # Todo
        #self.connect(self.bouton_pause, self.pause_play)
        #self.connexionEvent()

        # get the server information and player
        #self.connectInterface()
        #self.get_playerid()
        # then start the update process
        #self.update_now_is_playing()


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
            self.futureFunction)

    def onAction(self, action):
        """
        Catch button actions.

        ``action`` is an instance of :class:`xbmcgui.Action` class.
        """
        if action == ACTION_PREVIOUS_MENU:
            xbmc.log('Previous_menu' , xbmc.LOGNOTICE)
            self.quit_now_playing()

        elif action == ACTION_NAV_BACK:
            xbmc.log('nav_back' , xbmc.LOGNOTICE)
            self.quit_now_playing()

        elif action == ACTION_PAUSE : # currently it's the space on my keyboard
            xbmc.log('Action Pause', xbmc.LOGNOTICE)
            self.pause_play()
        
        elif action == ACTION_PLAY or action == ACTION_PLAYER_PLAY:
            xbmc.log('Action Play', xbmc.LOGNOTICE)
            self.pause_play()

        elif ( action == ACTION_VOLUME_DOWN )  or ( action == ACTION_VOLUME_UP ) :
            xbmc.log('Action Volume' , xbmc.LOGNOTICE)
            self.promptVolume()
        
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            xbmc.log('Action previous Menu', xbmc.LOGNOTICE)
            self.promptContextMenu()

        else:
            xbmc.log('else condition onAction in FramePlaying' , xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)


    def quit_now_playing(self):# todo : à tester
        self.NowIsPlaying = False       # with this flag the method update must exit the loop and stop
        self.WindowPlayinghere = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre now_is_playing is exiting: ' + str(self.WindowPlayinghere), xbmc.LOGNOTICE)
        self.connectInterface()
        self.get_playerid()
        #self.subscribe = Ecoute.Souscription(self.InterfaceCLI, self.playerid )
        #self.subscribe.resiliersouscription()
        self.InterfaceCLI.sendSignal('quit')
        xbmc.log('sendsignal quit in A quit() FramePlaying', xbmc.LOGNOTICE)
        # don't receive here because need in the answer of server to exit the update_now_is_playing()
        #recupropre = self.InterfaceCLI.receptionReponseEtDecodage()

        time.sleep(1)    # wait the server answer to unsubscribe so update function can exit the loop and stop
        #del subscribe
        self.threadRunning = False
        self.close()

    def pause_play(self):
        self.get_playerid()
        self.get_ident_server()
        self.connectInterface()

        if not self.flagStatePause:
            self.bouton_pause.setVisible(True)
            self.flagStatePause = True
            # pause also the subscribe
            self.subscribe = Ecoute.Souscription(self.InterfaceCLI,
                                                  self.playerid )
            self.subscribe.resiliersouscription()
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            self.InterfaceCLI.viderLeBuffer()
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
            # turn on the subscribe
            self.subscribe.subscription()

    def futureFunction(self):
        pass

    def promptVolume(self):
        # before call the windows volume turn off the subscribe
        self.connectInterface()
        self.get_playerid()
        self.subscribe = Ecoute.Souscription(self.InterfaceCLI, self.playerid )
        self.subscribe.resiliersouscription()
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        self.InterfaceCLI.viderLeBuffer()
        volumeFrame = outils.VolumeFrameChild()
        volumeFrame.doModal()
        self.subscribe = Ecoute.Souscription(self.InterfaceCLI, self.playerid )
        self.subscribe.subscription()
        del volumeFrame
        # then turn on the subscription
        del self.subscribe
        
    def promptContextMenu(self):
        contextMenuFrame = outils.ContextMenuFrameChild()
        contextMenuFrame.doModal()
        del contextMenuFrame

    def update_coverbox(self, lmsip, lmswebport, playerid, compteur):
        '''
        fonction qui devrait mettre à jour l'affichage de la pochette
        dans cette version on récupère la pochette du serveur pour le player courant
        dans une autre version on récupère la pochette du serveur grâce au tag fourni
        dans l'information sur la chanson en cours
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
        try:
            urllib.urlretrieve(urlcover , completeNameofFile)
            self.pochette.setImage(completeNameofFile)  # fonction d'xbmcgui
        except:
            debug('Erreur pour update coverbox in FramePlaying', xbmc.LOGNOTICE)

        #os.remove(completeNameofFile)  # suppression du fichier
        # fin fonction update_cover

    def connectInterface(self):
        self.InterfaceCLI = ConnexionClient.InterfaceCLIduLMS()


    def get_playerid(self):
        self.Players = outils.WhatAreThePlayers()
        self.playerid = self.Players.get_unplayeractif()

    def get_ident_server(self):
        self.Server = outils.WhereIsTheLMSServer()
        self.nomserver = self.Server.LMSnom
        self.lmsip = self.Server.LMSCLIip
        self.lmswebport = self.Server.LMSwebport

    def update_now_is_playing(self):
        ''' method to use with doModal() in the calling program, for exemple : in FrameMenu.fenetreMenu
            self.jivelette = FramePLaying.SlimIsPlaying()
            self.jivelette.doModal()
            or todo  the fonction is calling by the function calling
            self.jivelette.show()
            self.jivelette.update_now_is_playing()
            This is the main loop when display the Frame Slim is playing
            and the frame use doModal()
            thereis a similar method inside the class FrameMenu.fenetreMenu when the frame use show()
            but use a different logic to exit the loop
        '''
        xbmc.log('Entrée dans méthode Update_now_is_playing of FramePlaying', xbmc.LOGNOTICE)

        self.Window_is_playing = xbmcgui.getCurrentWindowId()
        #xbmc.log('fenetre de player en maj n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        #xbmc.log('nouvelle fenetre de player n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        # activation de la souscription au serveur process
        self.subscribe = Ecoute.Souscription(self.InterfaceCLI , self.playerid )
        self.subscribe.subscription()
        # todo Q : comment faire la gestion de l'arret de la boucle de souscription ?

        # there is no Abonnement in this class -> need to find something else
        while self.NowIsPlaying:    # this is a boolean flag
            time.sleep(0.5)

            timeoutdeTestdelaBoucle = time.time() + 60 * 2  # 2 minutes from now -for testing
            timeoutdeRecherchedesPlayers = time.time() + 60 * 20  #todo toutes les 20 minutes nous rechercherons les players
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
                    self.NowIsPlaying = True

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

                # Here the program is blocked until data come from network (receptionReponse) and are store
                # in recupropre
                recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
                xbmc.log( 'recupropre = ' + str(recupropre), xbmc.LOGNOTICE)
                # Then Analyse de la trame

                if 'subscribe:-' in recupropre:
                    xbmc.log('recu fin souscription in update in FramePlaying' , xbmc.LOGNOTICE)
                    self.NowIsPlaying = False
                    break
                xbmc.log( '2eme ligne, recupropre = ' + str(recupropre), xbmc.LOGNOTICE)

                if recupropre.startswith('quit'):
                    xbmc.log('recu quit in update in FramePlaying', xbmc.LOGNOTICE)
                    self.NowIsPlaying = False
                    break


                listeB = recupropre.split('subscribe:' + TIME_OF_LOOP_SUBSCRIBE +'|')
                # on élimine le début de la trame # attention doit correpondre à
                # la même valeur de subscribe dans Ecoute.py
                try:
                    textC = listeB[1]           # on conserve la deuximème trame après suscribe...
                except IndexError:
                    break
                listeRetour = textC.split('|')  # on obtient une liste des items
                dico = dict()                   # pour chaque élement de la liste sous la forme <val1>:<val2>
                dico2 = {}
                for x in listeRetour:           # on la place dans un dictionnaire
                    c = x.split(':')            # sous la forme  key: value et <val1> devient la key
                    if dico.has_key(c[0]):      # nous avons déjà une occurence
                        pass
                    else:
                        clef = c[0]
                        dico[clef] = c[1]       # ensuite on pourra piocher dans le dico la valeur
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
                    self.slider_duration.setPercent(pourcentagedureejouee)
                except KeyError:
                    pass

                try:
                    self.labelduree_jouee.setLabel(label= outils.getInHMS(dico['time']))
                except KeyError:
                    pass

                try:
                    self.labelduree_fin.setLabel(label= outils.getInHMS(dico['duration']))
                except KeyError:
                    self.labelduree_fin.setLabel(label= outils.getInHMS(0.0))

                # Todo : if it is a playlist it is not the same struct
                # so 'title' , 'time' and so on doesn't exist
                try:
                    nouveautitre = dico['title']
                except KeyError:
                    nouveautitre = ''
                    pass

                if not ( nouveautitre == titreenlecture ):

                    try:
                        self.labeltitre_1.reset()
                        self.labeltitre_1.addLabel(label='[B]' + dico['current_title'] + '[/B]')
                    except KeyError:
                        self.labeltitre_1.addLabel(label='')
                        pass

                    try:
                        titreenlecture = dico['title']
                        self.labeltitre_2.reset()
                        self.labeltitre_2.addLabel(label='[B]' + titreenlecture + '[/B]')
                    except KeyError:
                        self.labeltitre_2.addLabel(label='')

                    self.InterfaceCLI.sendtoCLISomething('album ?')
                    reponse  = self.InterfaceCLI.receptionReponseEtDecodage()
                    album = reponse.split('album|').pop()
                    self.labelAlbum.reset()
                    if not '|album' in album:
                        self.labelAlbum.addLabel(label='[B]' + album + '[/B]')

                    self.InterfaceCLI.sendtoCLISomething('artist ?')
                    reponse  = self.InterfaceCLI.receptionReponseEtDecodage()
                    artist = reponse.split('artist|').pop()
                    self.labelArtist.reset()
                    if not '|artist' in artist:
                        self.labelArtist.addLabel(label='[B]' + artist + '[/B]')

                self.update_coverbox(self.lmsip, self.lmswebport, self.playerid, compteur)

               # log pour voir
                compteur += 1
                timedutour = time.time()
                tempsparcouru = timedutour - timeEntreeDansLaBoucle
                xbmc.log(str(compteur) + ' tour de boucle : ' + str(tempsparcouru), xbmc.LOGDEBUG)
                xbmc.log('bool threadRunning : ' + str(self.threadRunning), xbmc.LOGNOTICE)
                if not self.threadRunning:          # must never happen because we are in the running thread
                    xbmc.log(' threadRunning is not True ', xbmc.LOGNOTICE)
                    self.breakBoucle_A = True
                    self.NowIsPlaying
            # fin de la boucle A : sortie de subscribe
        # fin boucle while NowIsPlaying
        xbmc.log('End of Boucle of Squueze , Bye', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        xbmc.log('Send resiliersouscription in A update now_is_playing() in FramePlaying', xbmc.LOGNOTICE)
        #del subscribe
        self.InterfaceCLI.viderLeBuffer()
        xbmc.log('End of fonction update_now_is_playing In FrmaePlaying, Bye', xbmc.LOGNOTICE)
    #fin fonction update_now_is_playing