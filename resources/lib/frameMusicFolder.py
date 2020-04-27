#!/usr/bin/env python
# -*- coding: utf-8 -*-



global Kodi
Kodi = True

#sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))

import threading
import time
import urllib
import os

from resources.lib import connexionClient, ecoute, framePlaying, outils
from resources.lib.ecoute import Souscription
from resources.lib import pyxbmctExtended


if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct

    
    ADDON = xbmcaddon.Addon()
    ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))
    ARTWORK_SLIM = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'Slimserver'))


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

    TIME_OF_LOOP_SUBCRIBE = ecoute.TIME_OF_LOOP_SUBSCRIBE

    global savepath
    savepath = xbmc.translatePath('special://temp')

    from resources.lib.outils import debug
    DEBUG_LEVEL = xbmc.LOGDEBUG

    TAGS = 'aCdejJKlstuwxy'


class ViewMusicFolder(pyxbmctExtended.BackgroundDialogWindow):

    def __init__(self, *args , **kwargs ):
        #title = args[0]
        super(ViewMusicFolder, self).__init__()

        self.recevoirEnAttente = threading.Event()
        self.recevoirEnAttente.clear()
        self.Abonnement = threading.Event()
        self.threadRunning = True
        self.WindowPlaying = xbmcgui.getCurrentWindowId()
        ('fenetre de class ViewMusicFolder n° : ' + str(self.WindowPlaying), DEBUG_LEVEL)

        self.geometrie()
        debug('geometrie set', DEBUG_LEVEL)
        self.controlMenus()
        debug('control Menu set', DEBUG_LEVEL)
        self.set_navigation()
        debug('navigation  set', DEBUG_LEVEL)

        # initial setup for playerid, lmsip, lmswebport etc...
        self.get_playerid()
        self.connectInterface()
        self.get_ident_server()
        debug('server : ' + self.nomserver + ' - ' + self.lmsip + ' : ' + self.lmswebport , DEBUG_LEVEL )
        debug('player : ' + self.playerid , DEBUG_LEVEL )

        self.InterfaceCLI.viderLeBuffer()


        self.connect(self.listMusicFolder,self.exploreOrPlay)

        self.connexionEvent()

        #self.connect(pyxbmct.ACTION_NAV_BACK, self.quit_listing) # rather self.close
        #self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self.quit_listing) # rather self.close


    def geometrie(self):
        # pyxbmct :
        SIZE_WIDTH_pyxbmct = 1280
        SIZE_HEIGHT_pyxbmct = 720
        self.tile_size = 20
        self.rows_bas = 3
        self.espace_bas = self.rows_bas * self.tile_size    # 3 rows from the bottom
        self.nbre_columns = SEIZE // 2
        SIZESCREEN_HEIGHT = xbmcgui.getScreenHeight()  # exemple  # 1080
        SIZESCREEN_WIDTH = xbmcgui.getScreenWidth()
        Size_W_ChildSelf = SIZE_WIDTH_pyxbmct // 2
        Size_H_ChildSelf = SIZE_HEIGHT_pyxbmct
        self.screenx = SIZESCREEN_WIDTH
        self.screeny = SIZESCREEN_HEIGHT
        debug('Real Size of Screen : ' + str(self.screenx) + ' x ' + str(self.screeny), DEBUG_LEVEL)
        if self.screenx > SIZE_WIDTH_pyxbmct:
            self.screenx = SIZE_WIDTH_pyxbmct
            self.screeny = SIZE_HEIGHT_pyxbmct

        self.setGeometry(width_=Size_W_ChildSelf,
                         height_=Size_H_ChildSelf - self.espace_bas ,
                         rows_= NEUF - self.rows_bas ,
                         columns_= self.nbre_columns  ,
                         pos_x= 1,
                         pos_y= 10 )

        debug('Size of Screen pyxbmct fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), DEBUG_LEVEL)

        self.image_dir = ARTWORK  # path to pictures used in the program (future development, todo)
        self.image_dir_slim = ARTWORK_SLIM
        self.cover_jpg = self.image_dir + '/music.png'  # pour le démarrage then updated
        self.image_background = self.image_dir + '/fond-noir.jpg'  # in next release could be change by users
        self.image_progress = self.image_dir + '/ajax-loader-bar.gif'  # not yet used, get from speedtest
        self.image_button_pause = self.image_dir + '/pause.png'  # get from Xsqueeze
        self.image_button_stop = self.image_dir + '/stop.png'  # get from Xsqueeze
        self.image_button_play = self.image_dir + '/play.png'  # get from Xsqueeze
        self.textureback_slider_duration = self.image_dir + '/slider_back.png'  # get from plugin audio spotify
        self.texture_slider_duration = self.image_dir + '/slider_button_new.png'
        self.image_list_focus = self.image_dir + '/MenuItemFO.png'  # myself
        self.image_folder = self.image_dir_slim + '/icon_folder.png'
        self.image_musique = self.image_dir + '/music.png'

    def controlMenus(self):
        ''' Fix the size of itemlists in menus lists'''

        self.title_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.title_label, 0 , 2 , 1 , 10)

        row_depart = 0
        col_depart = 0
        espace_row = NEUF - self.rows_bas
        espace_col = self.nbre_columns // 2
        hauteur_menu = 25

        self.listMusicFolder = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 40 , _imageHeight = 40 , _itemHeight=40)
        
        self.placeControl(self.listMusicFolder , row_depart , col_depart , espace_row, self.nbre_columns - 6 )

        # TRES IMPORTANT POUR AVOIR LE FOCUS
        # Add items to the list , need to ask the focus before filling the list from plugin.Plugin
        self.listMusicFolder.addItem('.')
        self.listMusicFolder.setEnabled(True)

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

    def onAction(self, action):
        """
        Catch button actions.

        ``action`` is an instance of :class:`xbmcgui.Action` class.
        """
        if action == ACTION_PREVIOUS_MENU:
            debug('Previous_menu' , DEBUG_LEVEL)
            self.quit_listing()
        elif action == ACTION_NAV_BACK:
            debug('nav_back' , DEBUG_LEVEL)
            self.quit_listing()
        else:
            debug('else condition onAction in frameMusicFolder' , DEBUG_LEVEL)
            self._executeConnected(action, self.actions_connected)

    def quit_listing(self):# todo : à tester
            self.WindowPlayinghere = xbmcgui.getCurrentWindowId()
            debug('fenetre listing is exiting: ' + str(self.WindowPlayinghere), DEBUG_LEVEL)
            self.connectInterface()
            self.get_playerid()
            self.InterfaceCLI.sendSignal('Quit')
            self.Abonnement.clear()
            self.threadRunning = False
            self.close()

    def set_navigation(self):

        # Set navigation between controls (Button, list or slider)
        # Control has to be added to a window first if not raise RuntimeError
        
        # todo : à revoir pour les autre menus (radios , favorites etc...
        # Set initial focus
        self.setFocus(self.listMusicFolder)
        
    def   list_Menu_Navigation(self):
        # todo écrire quoi faire quanq un item est sélectionné dans le listemenu
        # todo écrire quoi faire quand on bouge les flèches , la souris
        # à priori on veut juste naviguer entre les élements
        # ou bien selectionner l'action sur le menu
        # ce qui est fait par le connect
        self.listMusicFolder.setEnabled(True)

        if self.getFocus() == self.listMusicFolder:
            self.itemSelection1 = self.listMusicFolder.getListItem(
                self.listMusicFolder.getSelectedPosition()).getLabel()
            self.title_label.setLabel(self.itemSelection1)

    def exploreOrPlay(self):
        debug('Entrée dans la fonction eXploreOrPlay frameMusicFolder', DEBUG_LEVEL)

        labeitem = self.listMusicFolder.getListItem(self.listMusicFolder.getSelectedPosition()).getLabel()
        type = self.listMusicFolder.getListItem(self.listMusicFolder.getSelectedPosition()).getProperty('type')
        item_id = self.listMusicFolder.getListItem(self.listMusicFolder.getSelectedPosition()).getProperty('id')
        filename = self.listMusicFolder.getListItem(self.listMusicFolder.getSelectedPosition()).getProperty('filename')
        folder_parent_id = self.listMusicFolder.getListItem(self.listMusicFolder.getSelectedPosition()).getProperty('folder_parent_id')


        if type == 'folder':
            # explore this folder and open a new frame to print the result
            newFrame = ViewMusicFolder()
            newFrame.listMusicFolder.reset()

            requete =  'musicfolder 0 100 folder_id:' + item_id
            self.InterfaceCLI.sendtoCLISomething(requete)
            reception = self.InterfaceCLI.receptionReponseEtDecodage()
            '''
            for example : 
            musicfolder|0|100|folder_id:28999|
            id:5822|filename:01 Hugh Laurie - St. James Infirmary.mp3|type:track|
            id:5823|filename:02 Hugh Laurie - You Don't Know My Mind.mp3|type:track|
            [...]
            id:5836|filename:15 Hugh Laurie - Let Them Talk.mp3|type:track|
            count:15
            '''

            try:
                nbre_a_traiter = reception.split('count:')
            except ValueError:
                outils.functionNotYetImplemented()
                return

            try:
                nombreDItems = nbre_a_traiter.pop()
            except IndexError:
                outils.functionNotYetImplemented()
                return
            try:
                nbreEntier = int(nombreDItems)
            except:
                outils.functionNotYetImplemented()
                return

                # trim head and queue
            try:
                # poubelle, tampon = reponsepropre.split(TAGS+'|')
                poubelle, tampon = reception.split('musicfolder|0|100|')
                lesItemsDossiersNormalised, poubelle = tampon.split('|count:')
            except ValueError:
                return

            try:
                lachainedesItemsDossiers = lesItemsDossiersNormalised.split('|')  #
                debug('FrameMusicFolder:: Fleurs chainedesDossiers : ' + str(lachainedesItemsDossiers), DEBUG_LEVEL)
            except:
                debug('functionNotYetImplemented plugin_music::fleurs::Dossiers', DEBUG_LEVEL)
                outils.functionNotYetImplemented()
                return

            itemtampon = xbmcgui.ListItem()
            for chaine in lachainedesItemsDossiers:

                try:
                    clef, valeur = chaine.split(':', 1)
                except ValueError:
                    pass

                if clef == 'folder_id':
                    folder_parent_id = valeur
                    itemtampon.setProperty('folder_parent_id' , valeur)

                if clef == 'id':
                    itemtampon.setProperty(clef, valeur)
                    itemtampon.setProperty('folder_parent_id' , folder_parent_id)

                elif clef == 'filename':
                    itemtampon.setLabel(valeur)

                elif clef == 'type':
                    itemtampon.setProperty(clef, valeur)
                    if valeur == 'folder':
                        itemtampon.setArt({'thumb': self.image_folder})
                        debug('set art for folder',DEBUG_LEVEL)
                    elif valeur == 'track':
                        debug('set art for track',DEBUG_LEVEL)
                        requete = self.playerid + ' songinfo 0 20 track_id:' + itemtampon.getProperty('id') + ' tags:' + TAGS
                        self.InterfaceCLI.sendtoCLISomething(requete)
                        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                        chainereponse = reponse.split('|')
                        matching = [s for s in chainereponse if 'coverart:1' in s]
                        if matching:
                            coverartlist =  [s for s in chainereponse if 'artwork_track_id' in s]
                            try:
                                chainecoverart = coverartlist.pop()
                                chainecoverartlist = chainecoverart.split(':')
                                hascode_coverart = chainecoverartlist.pop()
                                filename_coverart = self.get_artwork(hashcode_artwork=hascode_coverart)
                                itemtampon.setArt({'thumb': filename_coverart})
                            except IndexError:
                                itemtampon.setArt({'thumb': self.image_musique})
                        else:
                            itemtampon.setArt({'thumb': self.image_musique})

                    newFrame.listMusicFolder.addItem(itemtampon)
                    itemtampon = xbmcgui.ListItem()

            newFrame.listMusicFolder.setVisible(True)
            newFrame.setFocus(newFrame.listMusicFolder)
            newFrame.doModal()
            xbmc.Monitor().waitForAbort()
            del newFrame
        # fin if folder

        elif type == 'track':
            track_id = item_id
            # Could play
            debug('launch to play : ' + filename + ' playlistcontrol cmd:load track_id:' + item_id,
                     DEBUG_LEVEL)

            choix = xbmcgui.Dialog().select(heading=filename, list=['Play Song now', \
                                                                       'Play folder now ', \
                                                                       'Play Song after the current song', \
                                                                       'Add Song  to Playlist', \
                                                                       'More Info'])

            if choix == 0:
                # exemple : playlistcontrol cmd:load album_id:1683
                requete = self.playerid + ' playlistcontrol cmd:load track_id:' + str(track_id)

            elif choix == 1:
                requete = self.playerid + ' playlistcontrol cmd:load folder_id:' + str(folder_parent_id)

            elif choix == 2:
                requete = self.playerid + ' playlistcontrol cmd:insert track_id:' + str(track_id)

            elif choix == 3:
                requete = self.playerid + ' playlistcontrol cmd:add track_id:' + str(track_id)

            if not choix < 0 and not choix > 3:
                debug('requete : ' + requete, DEBUG_LEVEL)

                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()


                # now it is going to play
                requetePlay = self.playerid + ' playlist play'
                self.InterfaceCLI.sendtoCLISomething(requetePlay)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                del reponse

                # then launch now is playing FramePlaying
                self.WindowPlaying = xbmcgui.getCurrentWindowId()
                debug('fenetre origine n° : ' + str(self.WindowPlaying), DEBUG_LEVEL)

                self.Abonnement.set()  # need to renew subscribe after interupt
                self.jivelette = framePlaying.SlimIsPlaying()

                # todo : test inversion show et doModal
                self.jivelette.show()
                self.jivelette.update_now_is_playing()
                # time.sleep(0.5)
                # self.update_now_is_playing()  # the loop that keep the jivelette stand showing

                # self.jivelette.doModal()
                del self.jivelette

            elif choix == 4:
                # need more stuff to dig songinfo
                requete = self.playerid + ' songinfo 0 100 track_id:' + str(track_id)
                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                try:
                    listesonginfo = reponse.split('|')
                except ValueError:
                    outils.functionNotYetImplemented()

                textInfo = ''
                for field in listesonginfo:

                    textInfo = textInfo +  field + '\r\n'

                dialogSongInfo = xbmcgui.Dialog()
                dialogSongInfo.textviewer('Song Info : ' + filename , textInfo )

            else:
                pass

        elif type == 'playlist':
            playlist_id = item_id
            # Could play
            debug('launch to play : ' + filename + ' playlistcontrol cmd:load playlist_id:' + item_id,
                     DEBUG_LEVEL)

            choix = xbmcgui.Dialog().select(heading=filename, list=['Play playlist now',
                                                                    'Play folder now ',
                                                                    'Play playlist after the current song'
                                                                    ] )

            if choix == 0:
                # exemple : playlistcontrol cmd:load album_id:1683
                requete = self.playerid + ' playlistcontrol cmd:load playlist_id:' + str(playlist_id)

            elif choix == 1:
                requete = self.playerid + ' playlistcontrol cmd:load folder_id:' + str(folder_parent_id)

            elif choix == 2:
                requete = self.playerid + ' playlistcontrol cmd:insert playlist_id:' + str(playlist_id)

            if not choix < 0 and not choix > 2 :
                debug('requete : ' + requete, DEBUG_LEVEL)

                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()

                # now it is going to play
                requetePlay = self.playerid + ' playlist play'
                self.InterfaceCLI.sendtoCLISomething(requetePlay)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                del reponse

                # then launch now is playing FramePlaying
                self.WindowPlaying = xbmcgui.getCurrentWindowId()
                debug('fenetre origine n° : ' + str(self.WindowPlaying), DEBUG_LEVEL)

                self.Abonnement.set()  # need to renew subscribe after interupt
                self.jivelette = framePlaying.SlimIsPlaying()

                # todo : test inversion show et doModal
                self.jivelette.show()
                self.jivelette.update_now_is_playing()
                # time.sleep(0.5)
                # self.update_now_is_playing()  # the loop that keep the jivelette stand showing

                # self.jivelette.doModal()
                del self.jivelette

            else:
                pass
    # fin fonction exploreOrPlay



    def launchPlayingItem(self, menudeprovenance): # this is a copy from frameList ? Todo Delete it here
        ''' when an app or a radio is selected  launch the command to play
        mainly : cmd playlist play item_id
        example : radioparadise playlist play item_id:25478.1
        we guess that we are in the menu_1, but not always true
        Todo extends to others menus
        except (=not audio or hasitem true)  we need to dig more -> open listmenu_2

        '''
        debug('entrée dans la function launchPlayingItem', DEBUG_LEVEL  )

        self.get_playerid()
        self.get_ident_server()
        if menudeprovenance == 'listMenu_1':

            labelajouer = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getLabel()
            #cmd = self.command
            #cmd = self.listMenu_ItemRadios.getListItem( self.listMenu_ItemRadios.getSelectedPosition()).getProperty('cmd')
            #cmd ='picks' ,  ....Radio, shoutcast ...
            cmd = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('cmd')
            item_id = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('id')
            audio_type = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('type')
            hasitems = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('hasitems')

        elif menudeprovenance == 'listMenu_2':
            labelajouer = self.listMenu_2.getListItem(self.listMenu_2.getSelectedPosition()).getLabel()
            #cmd = self.command
            #cmd = self.listMenu_ItemRadios.getListItem( self.listMenu_ItemRadios.getSelectedPosition()).getProperty('cmd')
            #cmd ='picks' ,  ....Radio, shoutcast ...
            # cmd comes from listMenu_1 it is not an error
            cmd = self.listMenu_1.getListItem(self.listMenu_1.getSelectedPosition()).getProperty('cmd')
            item_id = self.listMenu_2.getListItem(self.listMenu_2.getSelectedPosition()).getProperty('id')
            audio_type = self.listMenu_2.getListItem(self.listMenu_2.getSelectedPosition()).getProperty('type')
            hasitems = self.listMenu_2.getListItem(self.listMenu_2.getSelectedPosition()).getProperty('hasitems')


        debug('launch to play : ' + labelajouer + ' -> ' + cmd + ' playlist play item_id:' + item_id , DEBUG_LEVEL  )
        debug('parametre : ' + str(item_id)  + ' commande :  ' + cmd + ' type : ' + audio_type + ' hasitems ? ' + hasitems  , DEBUG_LEVEL  )

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
                debug('requete : ' + requete , DEBUG_LEVEL  )

                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                del reponse

                # then launch now is playing FramePlaying
                self.Abonnement.set() # need to renew subscribe after interupt
                self.jivelette = framePlaying.SlimIsPlaying()

                self.WindowPlaying = xbmcgui.getCurrentWindowId()
                debug('fenetre en cours n° : ' + str(self.WindowPlaying), DEBUG_LEVEL)

                # todo : test inversion show et doModal
                self.jivelette.show()

                #time.sleep(0.5)
                self.update_now_is_playing() # the loop that keep the jivelette stand showing

                #self.jivelette.doModal()
                del self.jivelette
            else:
                debug('not audio', DEBUG_LEVEL)
                pass

        else:
            # in normal condition it have not to be here because the test is done before
            # need to dig more and more and review the prévious step
            # todo because some radios or apps are link and need a new step to dig
            # copy/paste from Plugin menu_fleurs could do it ?
            self.listMenu_2.reset()
            self.connectInterface()
            self.InterfaceCLI.sendtoCLISomething(cmd + ' items  item_id:' + item_id +  ' count ')
            reponse =  self.InterfaceCLI.receptionReponseEtDecodage()
            texte_en_liste_a_traiter = reponse.split('|count:')
            debug('texte_a_traiter : ' +  str(texte_en_liste_a_traiter) , DEBUG_LEVEL )
            if texte_en_liste_a_traiter == ['']:
                # erreur dans la réponse
                outils.functionNotYetImplemented()
                return

            #exemple : ["00:04:20:17:1c:44|picks|items|0|count|item_id:46dc1389.0|title:Andy's Picks", '3']
            try:
                nombreDItemsapplications = texte_en_liste_a_traiter.pop()
            except IndexError:
                outils.functionNotYetImplemented()
                return
            texte_a_traiter_titre = texte_en_liste_a_traiter.pop()
            texte_en_liste_a_traiter_titre = texte_a_traiter_titre.split('title:')
            debug('texte_a_traiter titre: ' +  str(texte_en_liste_a_traiter_titre) , DEBUG_LEVEL )
            # exemple :  ['00:04:20:17:1c:44|picks|items|0|count|item_id:c4bca76a.0|', "Andy's Picks"]
            try:
                title = texte_en_liste_a_traiter_titre.pop()
            except IndexError:
                outils.functionNotYetImplemented()
            #if nombreDItemsapplications > 9:
            # turn 8 by 8 (step 8)
            #self.longListing.title_label.setLabel(title)
            self.title_label.setLabel(title)
            start = 0
            step = 8
            indicedesmenus = 1 # max = 4
            nbre_recolted = 0
            nbre_restant_a_recolter = int(nombreDItemsapplications)
            while nbre_recolted  < int(nombreDItemsapplications):
                #indicedesmenus = indicedesmenus + 1 # todo : à revoir pour incrémenter jusqu'à 4 listmenu
                if nbre_restant_a_recolter > step:
                    self.InterfaceCLI.sendtoCLISomething( cmd + ' items ' +  str(start) + '  '  + \
                                             str(step) + ' item_id:' +  str(item_id) )
                    reponsepropre = self.InterfaceCLI.receptionReponseEtDecodage()
                    debug('Les Fleurs unefoispropre : ' + str(reponsepropre) , DEBUG_LEVEL)
                    '''
                    exemple 1er tour : 00:04:20:17:1c:44|local|items|0|8|item_id:d4465007.0|title:Stations|
                    id:d4465007.0.0|name:Aquifm 98.0|type:audio|image:http://cdn-radiotime-logos.tunein.com/s296322q.png|isaudio:1|hasitems:0|
                    id:d4465007.0.1|name:ARL 92.9 (French Music)|type:audio|image:http://cdn-profiles.tunein.com/s25776/images/logoq.png|isaudio:1|hasitems:0|
                    id:d4465007.0.2|name:BFM Business 107.3 (French Talk)|type:audio|image:http://cdn-profiles.tunein.com/s17938/images/logoq.png|isaudio:1|hasitems:0|
                    id:d4465007.0.3|name:Blackbox 103.7 (Hip Hop Music)|type:audio|image:http://cdn-profiles.tunein.com/s50722/images/logoq.png?t=1|isaudio:1|hasitems:0|
                    id:d4465007.0.4|name:Chérie FM 95.3 (Adult Hits)|type:audio|image:http://cdn-profiles.tunein.com/s3124/images/logoq.png?t=1|isaudio:1|hasitems:0|
                    id:d4465007.0.5|name:élèctrodancefloor PARIS|type:audio|image:http://cdn-radiotime-logos.tunein.com/s293127q.png|isaudio:1|hasitems:0|
                    id:d4465007.0.6|name:Enjoy 33 92.6 (Top 40 & Pop Music)|type:audio|image:http://cdn-radiotime-logos.tunein.com/s50714q.png|isaudio:1|hasitems:0|
                    id:d4465007.0.7|name:Europe 1 104.6 (French Talk)|type:audio|image:http://cdn-radiotime-logos.tunein.com/s6566q.png|isaudio:1|hasitems:0|
                    count:50               
                    '''
                    lesItemsFleurs = reponsepropre.split('items|' + str(start) + '|' + str(step) + '|' )
                    debug('ligne 269 : ' + 'items|' + str(start) + '|' + str(step) + '|'  , DEBUG_LEVEL)
                    debug('ligne 270 : ' + str(lesItemsFleurs) , DEBUG_LEVEL)
                    nbre_recolted = nbre_recolted + step
                    nbre_restant_a_recolter = nbre_restant_a_recolter - step
                    start = start + step

                else: # moins d'items que le step
                    requete_construite = cmd + ' items ' +  str(start) + ' '  + str(nbre_restant_a_recolter) + ' item_id:' +  str(item_id)
                    self.InterfaceCLI.sendtoCLISomething( requete_construite )
                    reponsepropre = self.InterfaceCLI.receptionReponseEtDecodage()
                    debug('Les Fleurs unefoispropre : ' + str(reponsepropre) , DEBUG_LEVEL)
                    '''
                    exemple : 00:04:20:17:1c:44|picks|items|0|3|item_id:63d6bace.0|title:Andy's Picks|
                    id:63d6bace.0.0|name:Sofaspace Ambient Radio (Vorbis)|type:audio|isaudio:1|hasitems:0|
                    id:63d6bace.0.1|name:SomaFM - Groove Salad|type:audio|isaudio:1|hasitems:0|
                    id:63d6bace.0.2|name:Lounging Sound|type:audio|isaudio:1|hasitems:0|
                    count:3
                    '''
                    lesItemsFleurs = reponsepropre.split('items|' + str(start) + '|' + str(nbre_restant_a_recolter)  + '|' )
                    nbre_recolted = nbre_recolted + nbre_restant_a_recolter

                debug('la récolte a été bonne de  : ' + str(nbre_recolted) , DEBUG_LEVEL)

                #trim the count and trim the title
                lesItemsFleurs_text = lesItemsFleurs[1]
                debug('lesItemsFleurs_text : ' + lesItemsFleurs_text, xbmc.LOGDEBUG )
                index_du_count = lesItemsFleurs_text.find('|count:')
                debug('index count : ' + str(index_du_count), xbmc.LOGDEBUG )
                index_du_titre = lesItemsFleurs_text.find('title:')
                debug('index titre : ' + str(index_du_titre), xbmc.LOGDEBUG )
                index_du_fin_de_titre = lesItemsFleurs_text.find('|', index_du_titre)
                debug('index fin du  titre : ' + str(index_du_fin_de_titre), xbmc.LOGDEBUG )

                lesItemsFleursNormalised = lesItemsFleurs_text[index_du_fin_de_titre + 1 : index_du_count]
                debug('lesItemsFleursNormalised : ' + lesItemsFleursNormalised, DEBUG_LEVEL )
                '''
                exemple : 
                |id:3a7d1dbb.0.0|name:Sofaspace Ambient Radio (Vorbis)|type:audio|isaudio:1|hasitems:0|
                id:3a7d1dbb.0.1|name:SomaFM - Groove Salad|type:audio|isaudio:1|hasitems:0|
                id:3a7d1dbb.0.2|name:Lounging Sound|type:audio|isaudio:1|hasitems:0
                '''

                try:
                    lachainedesItemsFleurs = lesItemsFleursNormalised.split('|')#
                    debug('Frame: ' + str(lachainedesItemsFleurs) , DEBUG_LEVEL)
                except IndexError:
                    debug('frameMusicFolder.py : functionNotYetImplemented', DEBUG_LEVEL)
                    outils.functionNotYetImplemented()
                    return

                index = 0
                itemsFleur= [] # une liste
                itemtampon = xbmcgui.ListItem()
                #itemsFleur.append(itemtampon)
                for chaine in lachainedesItemsFleurs:
                    debug('ligne around 432 chaine d 1 item : ' + str(chaine), xbmc.LOGDEBUG)
                    clef, valeur = chaine.split(':', 1)

                    if clef == 'name':
                        #itemdeListe.setLabel(dictionnairedUnItemApp.get('name'))
                        #itemsFleur[index].setLabel(valeur)
                        itemtampon.setLabel(valeur)

                    elif clef == 'icon' or clef =='image':
                        ulricone = valeur
                        completeNameofFile = self.get_icon(index=itemtampon.getProperty('id'), urlicone= valeur)
                        #itemsFleur[index].setArt({'thumb': completeNameofFile})
                        #itemsFleur[index].setProperty('image' , completeNameofFile)
                        itemtampon.setArt({'thumb': completeNameofFile})
                        itemtampon.setProperty('image' , completeNameofFile)

                    elif clef == 'hasitems':
                        itemtampon.setProperty(clef, valeur)
                        itemtampon.setProperty('cmd' , cmd )
                        index = index + 1
                        itemsFleur.append(itemtampon)
                        itemtampon = xbmcgui.ListItem()

                    else:
                        itemtampon.setProperty(clef, valeur)

                for item in itemsFleur:
                    debug('ajout de item dans menu frameList::listMenu_2 : ' + item.getLabel() , DEBUG_LEVEL)
                    #self.longListing.ArrayOfMenu[indicedesmenus].addItem(item)
                    self.listMenu_2.addItem(item)


            #outils.functionNotYetImplemented()


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

    # copier/coller de la fonction de frameMenu.py
    def update_now_is_playing(self):
        '''copier/coller de la fonction de frameMenu.py'''

        self.Window_is_playing = xbmcgui.getCurrentWindowId()
        # debug('fenetre de player en maj n° : ' + str(self.WindowPlaying), xbmc.LOGDEBUG)
        # debug('nouvelle fenetre de player n° : ' + str(self.Window_is_playing), xbmc.LOGDEBUG)

        self.subscribe = Souscription(self.InterfaceCLI, self.playerid )
        self.subscribe.subscription()

        while self.Abonnement.is_set():  # remember Abonnement is an thread event for souscription
            time.sleep(0.5)

            timeoutdeTestdelaBoucle = time.time() + 60 * 2  # 2 minutes from now -for testing
            timeoutdeRecherchedesPlayers = time.time() + 60 * 20  # todo : futur develop toutes les 20 minutes nous rechercherons les players
            timeEntreeDansLaBoucle = time.time()
            compteur = 1
            titreenlecture = ''
            self.breakBoucle_A = False
            while (self.breakBoucle_A == False):  # Boucle A principale de Subscribe

                if time.time() > timeoutdeTestdelaBoucle:
                    debug('Timeout : break A  ', DEBUG_LEVEL)
                    break
                if not self.Abonnement.is_set:
                    break
                if xbmc.Monitor().waitForAbort(0.5):
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
                # debug('trame recue suite à suscribe : ' + str(pourLog), xbmc.LOGDEBUG)
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

                # Todo : analyse du bloc

                recupropre = self.InterfaceCLI.receptionReponseEtDecodage()

                if 'subscribe:-' in recupropre: # fin souscription the resiliersouscription is send by FramePlaying or
                                                # else diplaying
                                                # the FramePlaying  exits - function quit()
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
                    break

                try:
                    listeB = recupropre.split(
                        'subscribe:' + TIME_OF_LOOP_SUBCRIBE + '|')  # on élimine le début de la trame
                except ValueError:
                    continue

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
                    debug('percent duree : ' + str(pourcentagedureejouee) + ' - time: ' + dico['time'],
                             xbmc.LOGDEBUG)
                except KeyError:
                    pourcentagedureejouee = 0

                try:
                    self.jivelette.slider_duration.setPercent(pourcentagedureejouee)
                    # self.slider_duration.setPercent(pourcentagedureejouee)
                except KeyError:
                    pass

                try:
                    self.jivelette.labelduree_jouee.setLabel(label=outils.getInHMS(dico['time']))
                    # self.labelduree_jouee.setLabel(label= outils.getInHMS(self, dico['time']))
                except KeyError:
                    pass

                try:
                    self.jivelette.labelduree_fin.setLabel(label=outils.getInHMS(dico['duration']))
                    # self.labelduree_fin.setLabel(label= outils.getInHMS(self, dico['duration']))
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
                debug(str(compteur) + ' tour de boucle : ' + str(tempsparcouru), xbmc.LOGDEBUG)
                debug('bool jivelette.threadRunning : ' + str(self.jivelette.threadRunning), DEBUG_LEVEL)
                if not self.jivelette.threadRunning:
                    debug(' jivelette.threadRunning is not True ', DEBUG_LEVEL)
                    # self.subscribe.resiliersouscription() # double emploi
                    self.breakBoucle_A = True
                    self.Abonnement.clear()
            # fin de la boucle A : sortie de subscribe
        # fin boucle while
        debug('End of Boucle of Squeeze in FrameMusicFolder , Bye', DEBUG_LEVEL)
        self.subscribe.resiliersouscription()
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        debug('Send resiliersouscription in A update now_is_playing() in frameMusicFolder', DEBUG_LEVEL)
        self.InterfaceCLI.viderLeBuffer()
        debug('End of fonction update_now_is_playing in frameMusicFolder , Bye', DEBUG_LEVEL)
    # fin fonction update_now_is_playing

    def connectInterface(self):
        self.InterfaceCLI = connexionClient.InterfaceCLIduLMS()

    def get_playerid(self):
        self.Players = outils.WhatAreThePlayers()
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
        debug('filename icon : ' + str(completeNameofFile), xbmc.LOGDEBUG)

        if 'http' in urlicone:
            urltoopen = urlicone
        else:
            if urlicone.startswith('/'):
                debug('url icone avec /: ' + urlicone ,xbmc.LOGDEBUG )
            #urltoopen = 'http://' + self.origine.rechercheduserveur.LMSCLIip + ':' + self.origine.rechercheduserveur.LMSwebport + '/' + urlicone
                urltoopen = 'http://' + self.lmsip + ':' + self.lmswebport + urlicone
            else:
                debug('url icone sans /: ' + urlicone ,xbmc.LOGDEBUG )
                urltoopen = 'http://' + self.lmsip + ':' + self.lmswebport + '/' + urlicone
        try:
            urllib.urlretrieve(urltoopen, completeNameofFile)
        except IOError:
            outils.functionNotYetImplemented()
        debug('nom du fichier image : ' + completeNameofFile , DEBUG_LEVEL)
        return completeNameofFile
        # fin fonction fin fonction get_icon, class Plugin_Generique
        # test

    def get_artwork(self, hashcode_artwork):
        # http://<server>:<port>/music/<track_id>/cover.jpg
        filename = 'icon.image_' + str(hashcode_artwork) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)

        urlimage = 'http://' + self.lmsip + ':' + self.lmswebport + '/music/' + str(hashcode_artwork) + '/cover.jpg'

        try:
            urllib.urlretrieve(urlimage, completeNameofFile)
        except IOError:
            pass
            outils.functionNotYetImplemented()

        debug('nom du fichier image : ' + completeNameofFile, DEBUG_LEVEL)
        return completeNameofFile


        #self.dictionnairedesplayers = dict()
        #self.dictionnairedesplayers = self.Players.recherchedesPlayers(self.InterfaceCLI, self.recevoirEnAttente)
        # recherche d'un player actif et si actif vrai . actif = isplaying
        #self.actif , index_dictionnairedesPlayers ,  self.playerid = self.Players.playerActif(self.dictionnairedesplayers)
