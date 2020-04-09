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

from resources.lib import ConnexionClient , outils

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
    SEIZE = 16 * 4  #32 16 option
    NEUF =   9 * 4  #18 or 9

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

#@singleton : singleton doesn't work ->  TypeError: super() argument 1 must be type, not function
# no idea what that's is
class SlimIsPlaying(pyxbmct.AddonFullWindow):

    def __init__(self, *args ):
        title = args[0]
        super(SlimIsPlaying, self).__init__( title)

        self.threadRunning = True
        self.flagStatePause = False

        xbmc.log( ' param : ' + title  , xbmc.LOGNOTICE)

        self.WindowPlaying = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre de class SlimIsPlaying n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)

        # the Event : c'est là que cela se complique , doit-on communiquer avec le thread  interfaceduCLI (socket qui
        # envoie et reçoit  ?
        # ou bien communiquer simplement entre les fonctions dans le programme appelant ?
        # selon le modèle de conception de communication inter process : la programmation du code va changer
        # alors faire Attention et décrire le modèle et la logique retenue

        xbmc.log('Create Instance Slim is Now Playing KodiJivelette...' , xbmc.LOGNOTICE)

        SIZESCREEN_HEIGHT = xbmcgui.getScreenHeight()            # exemple  # 1080
        SIZESCREEN_WIDTH = xbmcgui.getScreenWidth()                         # 1920

        # replaced by pyxbmct but need for the size cover until the fix
        self.GRIDSCREEN_Y, Reste = divmod(SIZESCREEN_HEIGHT, 10)            # 108
        self.GRIDSCREEN_X, Reste = divmod(SIZESCREEN_WIDTH, 10)             # 192

        self.screenx = SIZESCREEN_WIDTH
        self.screeny = SIZESCREEN_HEIGHT
        xbmc.log('Real Size of Screen : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        if self.screenx > SIZE_WIDTH_pyxbmct:
            self.screenx = SIZE_WIDTH_pyxbmct
            self.screeny = SIZE_HEIGHT_pyxbmct

        #pyxbmct :
        self.setGeometry(self.screenx  , self.screeny , NEUF, SEIZE)
        xbmc.log('Size of Screen pyxbmct fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)

        # sizecover must be  a square
        #SIZECOVER_X  = int(self.GRIDSCREEN_X * 2.5)  # need to ask artWork size from server, adapt to the size screen
        SIZECOVER_X = int(self.screenx / SEIZE * 28 )
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

        self.textureback_slider_volume = self.image_dir + '/slider_back.png'
        self.texture_slider_volume = self.image_dir + '/slider_button_new.png'

        # reserve pour afficher cover.jpg
        self.pochette = pyxbmct.Image(self.cover_jpg)
        self.placeControl(self.pochette, 3 , int(SEIZE / 2) , 28 , 28 )  # to fix
        self.pochette.setImage(self.cover_jpg)

        # title of radio , apps songs ...
        self.labeltitre_1 = pyxbmct.FadeLabel( font= 'font50caps_title' , textColor ='0xFF888888' )
        self.placeControl(self.labeltitre_1,  8 , 4 , 3 , 27 )
        self.labeltitre_1.addLabel('')

        self.labeltitre_2 = pyxbmct.FadeLabel( font = 'font13', textColor ='0xFF888888' )
        self.placeControl(self.labeltitre_2, 12 , 4 , 2 , 27 )
        self.labeltitre_1.addLabel('')

        self.labelAlbum = pyxbmct.FadeLabel( font = 'font13', textColor ='0xFF888888' )
        self.placeControl(self.labelAlbum, 14 , 4 , 2 , 27 )
        self.labelAlbum.addLabel('')

        self.labelArtist = pyxbmct.FadeLabel( font = 'font13', textColor ='0xFF888888' )
        self.placeControl(self.labelArtist, 16 , 4 , 2 , 27 )
        self.labelArtist.addLabel('')

        # la boite de texte 2 carrés de large sur 8 de hauteur (test avec 3 -> pas assez d'espace)
        # attention qu'elle ne chevauche pas la playerbox
        self.textbox = pyxbmct.TextBox(textColor = '0xFF888888')
        self.placeControl(self.textbox, 15 , 1, 4 , 2 , 4 , 1)

        # Slider de la durée
        self.slider_duration = pyxbmct.Slider(textureback=self.textureback_slider_duration)
        self.placeControl(self.slider_duration, ligneButton - 2  , int((SEIZE / 2) + 5 )  , 1 , 18 , pad_x=1)
        #self.slider_duration = pyxbmct.Slider(textureback=self.textureback_slider_duration, buttonTexture=self.texture_slider_duration)
        #self.placeControl(self.slider_duration, ligneButton - 2  , int((SEIZE / 2) + 5 )  , 1 , 18 , pad_x = 5 , pad_y = 5 )

        self.slider_duration.setPercent(SLIDER_INIT_VALUE)

        # labels des durée
        self.labelduree_jouee = pyxbmct.Label('')
        self.placeControl(control=self.labelduree_jouee, row=ligneButton - 2 , column=int( SEIZE /2 ),  rowspan= 2 , columnspan = 5 , pad_x = 5 , pad_y = 5 )
        self.labelduree_fin = pyxbmct.Label('')
        self.placeControl(control=self.labelduree_fin,row= ligneButton - 2 , column=int( SEIZE /2 + 25), rowspan=2 ,columnspan= 4 , pad_x = 5 , pad_y = 5 )

        # no connect key

        # réserver la boite pour les infos sur le player, à ajuster selon retour expérience.
        self.playerbox = pyxbmct.TextBox()
        self.placeControl(self.playerbox, 1, 1 , 2 , 5 )

        # button pause :
        self.bouton_pause = pyxbmct.Button(label='', focusTexture=self.image_button_pause, noFocusTexture=self.image_button_pause)
        self.placeControl(control=self.bouton_pause, row = NEUF / 2 , column= int(SEIZE /2) - 5  , rowspan= 6 , columnspan= 6 )
        self.bouton_pause.setVisible(False)
        self.bouton_play = pyxbmct.Button(label='', focusTexture=self.image_button_play, noFocusTexture='')
        self.placeControl(self.bouton_play , row = NEUF / 2 , column= (SEIZE / 2 ) - 2  , rowspan= 6 , columnspan= 6 )
        self.bouton_play.setVisible(False)

        # Slider Volume :
        self.label_volume = pyxbmct.Label('' , alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(control=self.label_volume, row= ( NEUF / 2 )- 2 , column= ( SEIZE /2 ) - 15  , rowspan=2, columnspan=30)
        self.slider_volume = pyxbmct.Slider(textureback=self.textureback_slider_volume, texture=self.texture_slider_volume,
                                            texturefocus=self.textureback_slider_volume, orientation=xbmcgui.HORIZONTAL)
        self.placeControl(control=self.slider_volume , row = NEUF / 2  , column = ( SEIZE / 2 ) - 15  , rowspan = 3 , columnspan = 30  )
        self.label_volume.setVisible(False)
        self.slider_volume.setVisible(False)

        # zone de contrôle des actions
        self.connect(self.bouton_pause, self.pause_play)
        #self.connect(self.bouton_play, self.enleverpause)

        self.connexionEvent()

        self.connect(pyxbmct.ACTION_NAV_BACK, self.quit_now_playing) # rather self.close
        self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self.quit_now_playing) # rather self.close

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

        elif action == ACTION_VOLUME_UP : # it's the volume power (- +)  on my remote
            self.setVolume('UP')
        elif action == ACTION_VOLUME_DOWN:
            self.setVolume('DOWN')

        else:
            xbmc.log('else condition onAction' , xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)

    def connexionEventVolume(self):
        # Connect key and mouse events for list navigation feedback.
        self.connectEventList(
            [ACTION_VOLUME_UP,
             ACTION_VOLAMP_UP,
             ACTION_VOLUME_DOWN,
             ACTION_VOLAMP_DOWN],
            self.setVolume)

    def quit_now_playing(self):# todo : à tester
        self.WindowPlayinghere = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre now_is_playing is exiting: ' + str(self.WindowPlayinghere), xbmc.LOGNOTICE)
        #xbmc.log('fenetre enregistrée dans methode now_is_playing n° : ' + str(self.Window_is_playing), xbmc.LOGNOTICE) # attribute error here
        #self.Abonnement.clear() # -> AttributeError: 'SlimIsPlaying' object has no attribute 'Abonnement'
        # todo : tester appel fonction du prg principal
        # FrameMenu.fenetreMenu.desabonner() -> TypeError: unbound method desabonner() must be called with fenetreMenu
        # instance as first argument (got nothing instead)
        # self.subscribe.resiliersouscription() # -> AttributeError: 'SlimIsPlaying' object has no attribute subscribe
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

    def setVolume(self, UpOrDown):


        # need to know the actual volume in percent
        self.get_playerid()
        self.get_ident_server()
        self.connectInterface()
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








    #slider_duration    self.slider_volume.setPercent(pourcentage)

    def set_slider_duration(self, duree):
        self.slider_duration.setPercent(duree)

    def update_textbox(self, text):
        self.textbox.setText("\n".join(text))

    def update_playerbox(self, text):
        self.playerbox.setText(" ".join(text))

    def update_actionbox(self, text):
        self.actionbox.setText("\r".join(text))

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
        # bug on libreelec -> file system is read-only
        # so save in /tmp , construct the complete path
        # os.tmpfile() ??
        #savepath = xbmc.translatePath('special://temp')
        #savepath = '/tmp/'
        # savepath = 'special://temp'       # doesn't work
        filename = 'pochette' + str(compteur) + '.tmp'
        completeNameofFile = os.path.join(savepath , filename )
        xbmc.log('filename tmp : ' + str(completeNameofFile), xbmc.LOGNOTICE)
        urllib.urlretrieve(urlcover , completeNameofFile)
        # mise à jour de la pochette sur l'écran
        # fonctionne une seule fois , pourquoi ?
        self.pochette.setImage(completeNameofFile) # fonction d'xbmcgui
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