#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
just a try to get the menu Favorite in a separate window

'''

global Kodi
Kodi = True


import platform
import os
import sys
import urllib
import random
import threading
import time
import copy

from resources.lib import pyxbmctExtended
from resources.lib import ConnexionClient, Ecoute, FramePLaying, outils
from resources.lib.Ecoute import Souscription


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

    TIME_OF_LOOP_SUBCRIBE = Ecoute.TIME_OF_LOOP_SUBSCRIBE

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


sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))


class FavoritesMenu(pyxbmct.BlankDialogWindow):

    def __init__(self, *args ):

        super(FavoritesMenu, self).__init__()

        self.WindowPlaying = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre de class FavoritesMenu n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        xbmc.log('Create Instance FavoritesMenu...' , xbmc.LOGNOTICE)

        self.recevoirEnAttente = threading.Event()
        self.recevoirEnAttente.clear()
        self.Abonnement = threading.Event()
        self.threadRunning = True

        # pyxbmct :
        largeur = 300
        hauteur = 500
        self.setGeometry(largeur, hauteur, 2 , 10 , (1280 // 2)  - largeur , (720 // 2)  - (hauteur // 2) )
        xbmc.log('Size of Screen pyxbmct fix to : ' + str(largeur) + ' x ' + str(hauteur), xbmc.LOGNOTICE)

        self.image_dir = ARTWORK  # path to pictures used in the program
        self.image_list_focus = self.image_dir + '/MenuItemFO.png'        # get from myself
        self.listMenu_1 = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _itemHeight=40)
        self.placeControl(control=self.listMenu_1 , row=0  , column=0 , rowspan=10 , columnspan=10 )
        self.listMenu_1.addItem('test')

        self.connexionEvent()
        self.connect(self.listMenu_1, self.launchPlayingItem)

        self.setFocus(self.listMenu_1)


    def onAction(self, action):
        """
        Catch button actions.

        ``action`` is an instance of :class:`xbmcgui.Action` class.
        """
        if action == ACTION_PREVIOUS_MENU:
            xbmc.log('Previous_menu' , xbmc.LOGNOTICE)
            self.quit_listing()
        elif action == ACTION_NAV_BACK:
            xbmc.log('nav_back' , xbmc.LOGNOTICE)
            self.quit_listing()
        else:
            xbmc.log('else condition onAction' , xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)

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
            self.Menu_Navigation)

    def quit_listing(self):# todo : à tester
        self.WindowPlayinghere = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre listing is exiting: ' + str(self.WindowPlayinghere), xbmc.LOGNOTICE)

        self.Abonnement.clear()
        self.threadRunning = False
        self.close()

    def Menu_Navigation(self):
        # todo écrire quoi faire quand le menu est affiché
        pass

    def launchPlayingItem(self):
        ''' when a favorite is selected  launch the command to play
        mainly : cmd playlist play item_id
        example : radioparadise playlist play item_id:25478.1
        we guess that we are in the menu_1, but not always true
        '''

        self.get_playerid()
        self.get_ident_server()

        labelajouer = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getLabel()
        cmd = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('cmd')
        item_id = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('id')
        audio_type = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('type')
        hasitems = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('hasitems')

        xbmc.log('launch to play : ' + labelajouer + ' -> ' + cmd + ' playlist play item_id:' + item_id , xbmc.LOGNOTICE  )
        xbmc.log('parametre : ' + str(item_id)  + ' commande :  ' + cmd + ' type : ' + audio_type + ' hasitems ? ' + hasitems  , xbmc.LOGNOTICE  )

        if audio_type == 'audio' and hasitems == '0':

            choix = xbmcgui.Dialog().select(heading= labelajouer, list= ['Play now', 'Play after the current song' ,  'Add to Playlist' ])
            if choix == 0:
                requete = cmd + ' playlist play item_id:' + str(item_id)
            elif choix == 1:
                requete = cmd + ' playlist insert item_id:' + str(item_id)
            elif choix == 2:
                requete = cmd + ' playlist add item_id:' + str(item_id)

            if not choix < 0:
                self.connectInterface()
                xbmc.log('requete : ' + requete , xbmc.LOGNOTICE  )

                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                del reponse

                # then launch now is playing FramePlaying
                self.Abonnement.set() # need to renew subscribe after interupt
                self.jivelette = FramePLaying.SlimIsPlaying()

                self.WindowPlaying = xbmcgui.getCurrentWindowId()
                xbmc.log('fenetre en cours n° : ' + str(self.WindowPlaying), xbmc.LOGNOTICE)

                # todo : test inversion show et doModal
                self.jivelette.show()

                #time.sleep(0.5)
                self.update_now_is_playing() # the loop that keep the jivelette stand showing

                #self.jivelette.doModal()
                del self.jivelette
            else:
                # cancel asked
                pass
    # fin fonction launchPlayingItem

    # copier/coller de la fonction de FrameMenu.py
    def update_now_is_playing(self):
        '''copier/coller de la fonction de FrameMenu.py'''

        self.Window_is_playing = xbmcgui.getCurrentWindowId()

        self.subscribe = Souscription(self.InterfaceCLI, self.playerid, self.Abonnement, self.recevoirEnAttente)
        self.subscribe.subscription()

        while self.Abonnement.is_set():  # remember Abonnement is an thread event for souscription
            time.sleep(0.5)
            timeoutdeTestdelaBoucle = time.time() + 60 * 2  # 2 minutes from now -for testing
            timeoutdeRecherchedesPlayers = time.time() + 60 * 20  # todo : futur develop toutes les 20 minutes nous rechercherons les players
            timeEntreeDansLaBoucle = time.time()
            compteur = 1
            titreenlecture = ''
            self.breakBoucle_A = False
            timeoutduVolume = time.time() + 20
            while (self.breakBoucle_A == False):  # Boucle A principale de Subscribe

                if time.time() > timeoutdeTestdelaBoucle:
                    xbmc.log('Timeout : break A  ', xbmc.LOGNOTICE)
                    break
                if not self.Abonnement.is_set:
                    break
                if xbmc.Monitor().waitForAbort(0.5):
                    self.breakBoucle_A = True
                    self.Abonnement.clear()

                recupropre = self.InterfaceCLI.receptionReponseEtDecodage()
                listeB = recupropre.split(
                    'subscribe:' + TIME_OF_LOOP_SUBCRIBE + '|')  # on élimine le début de la trame
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
                    self.jivelette.slider_duration.setPercent(pourcentagedureejouee)
                except KeyError:
                    pass

                try:
                    self.jivelette.labelduree_jouee.setLabel(label=outils.getInHMS(dico['time']))
                except KeyError:
                    pass

                try:
                    self.jivelette.labelduree_fin.setLabel(label=outils.getInHMS(dico['duration']))
                except KeyError:
                    self.jivelette.labelduree_fin.setLabel(label=outils.getInHMS(0.0))

                try:
                    nouveautitre = dico['title']
                except KeyError:
                    pass

                if not nouveautitre == titreenlecture:

                    try:
                        self.jivelette.labeltitre_1.reset()
                        self.jivelette.labeltitre_1.addLabel(label='[B]' + dico['current_title'] + '[/B]')
                    except KeyError:
                        self.jivelette.labeltitre_1.reset()
                        pass

                    try:
                        titreenlecture = dico['title']
                        self.jivelette.labeltitre_2.reset()
                        self.jivelette.labeltitre_2.addLabel(label='[B]' + titreenlecture + '[/B]')
                    except KeyError:
                        self.jivelette.labeltitre_2.reset()

                    self.InterfaceCLI.sendtoCLISomething('album ?')
                    reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                    album = reponse.split('album|').pop()
                    self.jivelette.labelAlbum.reset()
                    if not '|album' in album:
                        self.jivelette.labelAlbum.addLabel(label='[B]' + album + '[/B]')

                    self.InterfaceCLI.sendtoCLISomething('artist ?')
                    reponse = self.InterfaceCLI.receptionReponseEtDecodage()
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
                    # self.subscribe.resiliersouscription() # double emploi
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
            # fin de la boucle A : sortie de subscribe
        # fin boucle while
        xbmc.log('End of Boucle of Squueze , Bye', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        time.sleep(0.2)
        xbmc.log('End of fonction update_now_is_playing , Bye', xbmc.LOGNOTICE)
    # fin fonction update_now_is_playing

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
