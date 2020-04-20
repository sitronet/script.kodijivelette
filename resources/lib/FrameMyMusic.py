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
class MyMusicPlugin(pyxbmctExtended.BackgroundDialogWindow):

    def __init__(self, *args , **kwargs ):
        #title = args[0]
        super(MyMusicPlugin, self).__init__()

        self.recevoirEnAttente = threading.Event()
        self.recevoirEnAttente.clear()
        self.Abonnement = threading.Event()
        self.threadRunning = True
        self.WindowPlaying = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre de class MyMusicPlugin n° : ' + str(self.WindowPlaying), xbmc.LOGNOTICE)
        xbmc.log('Create Instance MyMusicPlugin KodiJivelette...' , xbmc.LOGNOTICE)
        self.playerid = ''

        self.geometrie()
        xbmc.log('geometrie set', xbmc.LOGNOTICE)
        self.controlMenus()
        xbmc.log('control set', xbmc.LOGNOTICE)
        self.set_navigation()
        xbmc.log('navigation  set', xbmc.LOGNOTICE)

        self.connexionEvent()

        self.connect(self.listMenu_allArtists, lambda : self.f_detailAlbums(menudeprovenance='listMenu_allArtists'))
        self.connect(self.listMenu_allAlbums, self.f_allAlbums_details)
        self.connect(self.listMenu_detailAlbums, lambda : self.f_listeTracks(menudeprovenance='listMenu_detailAlbums'))
        self.connect(self.listMenu_playlist, self.f_detailItemPlaylist)

        self.connect(pyxbmct.ACTION_NAV_BACK, self.quit_listing) # rather self.close
        self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self.quit_listing) # rather self.close


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
            self.screenx = SIZE_WIDTH_pyxbmct
            self.screeny = SIZE_HEIGHT_pyxbmct

        self.image_dir = ARTWORK  # path to pictures used in the program (future development, todo)

        self.cover_jpg = self.image_dir + '/music.png'  # pour le démarrage then updated
        self.image_background = self.image_dir + '/fond-noir.jpg'  # in next release could be change by users
        self.image_button_pause = self.image_dir + '/pause.png'  # get from Xsqueeze
        self.image_button_stop = self.image_dir + '/stop.png'  # get from Xsqueeze
        self.image_button_play = self.image_dir + '/play.png'  # get from Xsqueeze

        self.textureback_slider_duration = self.image_dir + '/slider_back.png'  # get from plugin audio spotify
        self.texture_slider_duration = self.image_dir + '/slider_button_new.png'

        self.image_list_focus = self.image_dir + '/MenuItemFO.png'  # myself

        #pyxbmct :
        self.setGeometry(self.screenx  , self.screeny , NEUF, SEIZE)
        xbmc.log('Size of Screen pyxbmct fix to : ' + str(self.screenx) + ' x ' + str(self.screeny), xbmc.LOGNOTICE)
        # cover when playing
        #SIZECOVER_X = int(self.screenx / SEIZE * 28 )
        SIZECOVER_X = (SEIZE // 2) - 6
        self.sizecover_x = SIZECOVER_X
        #SIZECOVER_Y = self.GRIDSCREEN_Y * 3  # and reserve a sized frame to covers,attention SIZECOVER_X != SIZECOVER_Y
        xbmc.log('Taille pochette : ' + str(SIZECOVER_X) + ' x ' + str(SIZECOVER_X) , xbmc.LOGNOTICE)

        ligneButton = NEUF - 3
        SLIDER_INIT_VALUE = 0
        # reserve pour afficher cover.jpg
        self.cover_jpg = self.image_dir + '/vinyl.png'      # pour le démarrage then updated
        # need some adjustment
        # reserve pour afficher cover.jpg
        self.pochette = pyxbmct.Image(self.cover_jpg)
        self.placeControl(control=self.pochette,
                          row=3,
                          column=(SEIZE // 2) ,
                          rowspan=28,
                          columnspan=29)  # todo to fix
        self.pochette.setImage(self.cover_jpg)

        # Slider de la durée
        self.slider_duration = pyxbmct.Slider(textureback=self.textureback_slider_duration)
        self.placeControl(control=self.slider_duration,
                          row=ligneButton - 2,
                          column=(SEIZE // 2),
                          rowspan=1,
                          columnspan=29 - 2,
                          pad_x=1)

        self.slider_duration.setPercent(SLIDER_INIT_VALUE)

        # labels des durée
        self.labelduree_jouee = pyxbmct.Label('',textColor ='0xFF808080')
        self.placeControl(control=self.labelduree_jouee,
                          row=ligneButton - 2,
                          column=(SEIZE // 2) ,
                          rowspan=2,
                          columnspan=5,
                          pad_x=5,
                          pad_y=5)
        self.labelduree_fin = pyxbmct.Label('',textColor ='0xFF888888')
        self.placeControl(control=self.labelduree_fin,
                          row=ligneButton - 2,
                          column=(SEIZE // 2) + (29 - 5),
                          rowspan=2,
                          columnspan=4,
                          pad_x=5,
                          pad_y=5)



    def controlMenus(self):
        ''' Fix the size of itemlists in menus lists'''

        self.title_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.title_label, 0 , 2 , 1 , 10)

        row_depart = 2
        col_depart = 0
        espace_row = 35
        espace_col = SEIZE / 4
        hauteur_menu = 25

        self.listMenu_allArtists = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 40 , _imageHeight = 40 , _itemHeight=42)
        self.listMenu_allAlbums = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 40 , _imageHeight = 40 , _itemHeight=42)

        self.listMenu_detailAlbums = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 0 , _imageHeight = 0 , _itemHeight=30)

        self.listMenu_playlist = pyxbmct.List(buttonFocusTexture=self.image_list_focus, _imageWidth= 40 , _imageHeight = 40 , _itemHeight=42)

        self.placeControl(self.listMenu_allArtists , row_depart , col_depart  , espace_row, espace_col )
        
        self.placeControl(self.listMenu_allAlbums, row_depart, col_depart, espace_row, espace_col)

        self.placeControl(self.listMenu_detailAlbums , row_depart , col_depart + espace_col, espace_row, espace_col )

        self.placeControl(self.listMenu_playlist , row_depart , col_depart  , espace_row, (SEIZE / 2) - 2 )

        # TRES IMPORTANT POUR AVOIR LE FOCUS
        # Add items to the list , need to ask the focus before filling the list from Plugin.Plugin
        self.listMenu_allArtists.addItem('.')
        self.listMenu_allAlbums.addItem('.')
        self.listMenu_playlist.addItem('.')

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
            xbmc.log('Previous_menu' , xbmc.LOGNOTICE)
            self.quit_listing()
        elif action == ACTION_NAV_BACK:
            xbmc.log('nav_back' , xbmc.LOGNOTICE)
            self.quit_listing()
        else:
            xbmc.log('else condition onAction in FrameMyMusic' , xbmc.LOGNOTICE)
            self._executeConnected(action, self.actions_connected)

    def quit_listing(self):# todo : à tester
        self.WindowPlayinghere = xbmcgui.getCurrentWindowId()
        xbmc.log('fenetre listing is exiting: ' + str(self.WindowPlayinghere), xbmc.LOGNOTICE)
        #xbmc.log('fenetre enregistrée dans methode now_is_playing n° : ' + str(self.Window_is_playing), xbmc.LOGNOTICE) # attribute error here
        #self.Abonnement.clear() # -> AttributeError: 'SlimIsPlaying' object has no attribute 'Abonnement'
        # todo : tester appel fonction du prg principal
        # FrameMenu.fenetreMenu.desabonner() -> TypeError: unbound method desabonner() must be called with fenetreMenu
        # instance as first argument (got nothing instead)
        # self.subscribe.resiliersouscription() # -> AttributeError: 'SlimIsPlaying' object has no attribute subscribe
        self.connectInterface()
        self.get_playerid()
        self.subscribe = Ecoute.Souscription(self.InterfaceCLI, self.playerid)
        self.subscribe.resiliersouscription()
        # doit on récupérer la réponse ?
        self.Abonnement.clear()
        self.threadRunning = False
        self.close()

    def set_navigation(self):

        # Set navigation between controls (Button, list or slider)
        # Control has to be added to a window first if not raise RuntimeError

        self.listMenu_allArtists.controlRight(self.listMenu_detailAlbums)
        self.listMenu_detailAlbums.controlRight(self.listMenu_allArtists)
        
        self.listMenu_allAlbums.controlRight(self.listMenu_detailAlbums)

        #self.listMenu_allArtists.controlLeft(self.listMenu_detailAlbums)
        self.listMenu_detailAlbums.controlLeft(self.listMenu_allArtists)

        # Set initial focus , don't forget to fill an item before setfocus
        #self.setFocus(self.listMenu_allArtists)
        
    def   list_Menu_Navigation(self):
        # todo écrire quoi faire quanq un item est sélectionné dans le listemenu
        if self.getFocus() == self.listMenu_allArtists:
            self.itemSelection = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getLabel()
            self.title_label.setLabel(self.itemSelection)
        
        elif self.getFocus() == self.listMenu_allAlbums:
            self.itemSelectiondetail = self.listMenu_allAlbums.getListItem(
                                self.listMenu_allAlbums.getSelectedPosition()).getLabel()
            self.title_label.setLabel(self.itemSelectiondetail)

        elif self.getFocus() == self.listMenu_detailAlbums:
            self.itemSelectiondetail = self.listMenu_detailAlbums.getListItem(
                                self.listMenu_detailAlbums.getSelectedPosition()).getLabel()
            self.title_label.setLabel(self.itemSelectiondetail)

    def launchArtists(self, menudeprovenance='allArtists'):
        pass

    def f_allAlbums_details(self):
        self.get_playerid()
        self.get_ident_server()
        self.connectInterface()
        self.listMenu_detailAlbums.reset()

        labelajouer = self.listMenu_allAlbums.getListItem(self.listMenu_allAlbums.getSelectedPosition()).getLabel()
        try:
            artist = self.listMenu_allAlbums.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty(
            'artist')
        except:
            pass
        self.title_label.setLabel(labelajouer)

        # retrieve the filename cover.jpg from previous menulist and print it on coverbox
        file_image = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty(
            'image')
        if file_image:
            self.pochette.setImage(file_image)

        album_id = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty(
            'id')
        try:
            artist_id = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty(
            'artist_id')
        except:
            pass
        requete = 'tracks 0 100 ' + 'album_id:' + album_id + ' sort:tracknum ' + 'tags:' + TAGS

        self.InterfaceCLI.viderLeBuffer()
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()

        #enlever entête et queue
        texte_en_liste_a_traiter = reponse.split('|count:')
        xbmc.log('texte_a_traiter : ' + str(texte_en_liste_a_traiter), xbmc.LOGNOTICE)
        if texte_en_liste_a_traiter == ['']:
            # erreur dans la réponse
            self.functionNotYetImplemented()
            return

        try:
            nombreDItemsTracks = texte_en_liste_a_traiter.pop()
        except IndexError:
            self.functionNotYetImplemented()
            return
        try:
            texte_a_traiter_titre = texte_en_liste_a_traiter.pop()
            texte_en_liste_a_traiter_entete = texte_a_traiter_titre.split('tags:' + TAGS + '|')
            xbmc.log('texte_a_traiter titre: ' + str(texte_en_liste_a_traiter_entete), xbmc.LOGNOTICE)
        except IndexError:
            item = xbmcgui.ListItem()
            item.setLabel('Get an Error from Server! ')
            self.listMenu_detailAlbums.addItem(item)

            return
        # exemple :
        try:
            lesItemsTracksNormalised = texte_en_liste_a_traiter_entete[1]
            xbmc.log('lesItemsTracksNormalised : ' + lesItemsTracksNormalised, xbmc.LOGNOTICE)
        except IndexError:
            return

        try:
            lachainedesItemsTracks = lesItemsTracksNormalised.split('|')  #
            xbmc.log('detail Albums : ' + str(lachainedesItemsTracks), xbmc.LOGNOTICE)
        except IndexError:
            xbmc.log('functionNotYetImplemented detailAlbums ', xbmc.LOGNOTICE)
            self.functionNotYetImplemented()
            return


        secondEtsuivant = False
        index = 0
        indice = ''  # fix if tracknum doesn't exist
        titre = ''
        year = ''
        duree = ''
        itemsTracks = []  # une liste
        itemtampon = xbmcgui.ListItem()
        for chaine in lachainedesItemsTracks:
            xbmc.log('detail album 1 item : ' + str(chaine), xbmc.LOGNOTICE)
            try:
                clef, valeur = chaine.split(':', 1)
            except ValueError:
                # probably there are some ':' in the chaine (lyrics or information around the title)
                # so we go on anyway
                pass

            if clef == 'id':

                if secondEtsuivant:
                    itemtampon.setLabel(indice + ' - ' + titre + ' - ' + year + ' : ' + duree + ' .')
                    itemtampon.setProperty('album_id', album_id)
                    try:
                        itemtampon.setProperty('artist_id', artist_id)
                    except:
                        pass
                    itemsTracks.append(itemtampon)
                    itemtampon = xbmcgui.ListItem()
                    index = index + 1
                    xbmc.log('Ajout de l item dans listItem tampon' + titre + ' ' + itemtampon.getProperty('track_id'),
                             xbmc.LOGNOTICE)

                itemtampon.setProperty('track_id', valeur)
                secondEtsuivant = True

            elif clef == 'title':
                titre = valeur
                # itemtampon.setLabel(valeur)

            elif clef == 'duration':
                duree = outils.getInHMS(valeur)

            elif clef == 'artwork_track_id':
                hascode_artwork = valeur
                completeNameofFile = self.get_artwork(hashcode_artwork=hascode_artwork)
                # itemtampon.setArt({'thumb': completeNameofFile})
                itemtampon.setProperty('image', completeNameofFile)

            elif clef == 'tracknum':
                itemtampon.setProperty(clef, valeur)
                indice = valeur

            elif clef == 'year':
                itemtampon.setProperty(clef, valeur)
                year = valeur
            else:
                # not sure that we have to keep other value
                # for now we keep them but todo pass them
                itemtampon.setProperty(clef, valeur)

        # once exit the loop 'for' , fill the list with the last itemtampon :
        itemtampon.setProperty('album_id', album_id)
        itemtampon.setProperty('artist_id', artist_id)
        itemtampon.setLabel(indice + ' - ' + titre + ' - ' + year + ' : ' + duree + ' .')
        itemsTracks.append(itemtampon)
        xbmc.log('Ajout de l item dans listItem tampon ' + titre + ' ' + itemtampon.getProperty('track_id'),
                 xbmc.LOGNOTICE)

        # sort the itemsTracks list by tracknum todo test this function or similar
        # sorted(itemsTracks, key=lambda tracknum: tracknum[1])   # sort by n° track not always true

        for item in itemsTracks:
            xbmc.log('ajout de item trackss dans menu detailAlbum  : ' + item.getLabel(), xbmc.LOGNOTICE)
            self.listMenu_detailAlbums.addItem(item)
    # fin fonction f_allAlbums_details

    def f_detailAlbums(self, menudeprovenance):
        self.get_playerid()
        self.get_ident_server()
        self.connectInterface()
        self.listMenu_detailAlbums.reset()

        labelajouer = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getLabel()
        artist = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty('artist')
        self.title_label.setLabel(labelajouer)

        # retrieve the filename cover.jpg from previous menulist and print it on coverbox
        file_image = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty('image')
        if file_image:
            self.pochette.setImage(file_image)
        
        album_id = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty('id')
        artist_id = self.listMenu_allArtists.getListItem(self.listMenu_allArtists.getSelectedPosition()).getProperty('artist_id')
        requete = 'tracks 0 100 artist_id:' + artist_id + ' album_id:' + album_id + ' sort:tracknum ' + 'tags:' + TAGS

        self.InterfaceCLI.viderLeBuffer()
        self.InterfaceCLI.sendtoCLISomething(requete)
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        '''exemple de reponse :
        tracks|0|100|artist_id:4216|album_id:1683|tags:aCdejJKlstuwxy|
        id:20179|title:Au pays des Merveilles de Juliet|artist:Yves Simon|compilation:0|duration:144.144|
        album_id:1683|coverart:1|artwork_track_id:afe480cb|album:Au Pays Des Merveilles De Juliet|artist_id:4216|tracknum:3|
        url:file:///i-data/e0c90389/music/Musique/Yves%20Simon/03%20Au%20pays%20des%20Merveilles%20de%20Juliet.flac|
        remote:0|year:2007|
        
        [...]
        id:20178|title:Rue de la Huchette|artist:Yves Simon|compilation:0|duration:139.808|album_id:1683|coverart:1|
        artwork_track_id:afe480cb|album:Au Pays Des Merveilles De Juliet|artist_id:4216|tracknum:2|
        url:file:///i-data/e0c90389/music/Musique/Yves%20Simon/02%20Rue%20de%20la%20Huchette.flac|
        remote:0|year:2007|
        count:10
        
        '''

        # enlever entête et queue
        texte_en_liste_a_traiter = reponse.split('|count:')
        xbmc.log('texte_a_traiter : ' +  str(texte_en_liste_a_traiter) , xbmc.LOGNOTICE )
        if texte_en_liste_a_traiter == ['']:
            # erreur dans la réponse
            self.functionNotYetImplemented()
            return

        try:
            nombreDItemsTracks = texte_en_liste_a_traiter.pop()
        except IndexError:
            self.functionNotYetImplemented()
            return
        try:
            texte_a_traiter_titre = texte_en_liste_a_traiter.pop()
            texte_en_liste_a_traiter_entete = texte_a_traiter_titre.split('tags:' + TAGS + '|' )
            xbmc.log('texte_a_traiter titre: ' +  str(texte_en_liste_a_traiter_entete) , xbmc.LOGNOTICE )
        except IndexError:
            item = xbmcgui.ListItem()
            item.setLabel('Get an Error from Server! ')
            self.listMenu_detailAlbums.addItem(item)

            return
        # exemple :
        try:
            lesItemsTracksNormalised = texte_en_liste_a_traiter_entete[1]
            xbmc.log('lesItemsTracksNormalised : ' + lesItemsTracksNormalised, xbmc.LOGNOTICE )
        except IndexError:
            return

        try:
            lachainedesItemsTracks = lesItemsTracksNormalised.split('|') #
            xbmc.log('detail Albums : ' + str(lachainedesItemsTracks) , xbmc.LOGNOTICE)
        except IndexError:
            xbmc.log('functionNotYetImplemented detailAlbums 310', xbmc.LOGNOTICE)
            self.functionNotYetImplemented()
            return
        '''
        exemple detail albums :
        ['id:23528', 'title:Allende', 'artist:1984 - En public au Theatre des Champs Elysees', 'compilation:0', 
        'duration:270.367', 'album_id:1967', 'coverart:0', 'album:Cd3', 'artist_id:4425', 'tracknum:23', 
        'url:file:///i-data/e0c/music/TOUT_Leo_Ferre_ou_Presque...48_CD_et_Extras/nde.mp3', 'remote:0',
         'year:0', 
         'id:23531', 'title:Avec le temps', 'artist:1984 - En public au Theatre des Champs Elysees', 'compilation:0', 
         'duration:169.795', 'album_id:1967', 'coverart:0', 'album:Cd3', 'artist_id:4425', 'tracknum:26', 
         'url:file:///i-data/e0c/music/TOUT_Leo_Ferre_ou_Presque...48_CD_et_Extra', 
         'remote:0', 'year:0', 
         [...]
         , 'id:23529', 'title:Words Words Words', 'artist:1984 - En public au Theatre des Champs Elysees', 'compilation:0',
          'duration:219.689', 'album_id:1967', 'coverart:0', 'album:Cd3', 'artist_id:4425', 'tracknum:24', 
          'url:file:///i-data/e0c/music/TOUT_Leo_Ferre_ou_Presque...48_CD_et_Extrasrds.mp3', 
          'remote:0', 'year:0']  
        
        '''
        secondEtsuivant = False
        index = 0
        indice ='' # fix if tracknum doesn't exist
        titre=''
        year=''
        duree = ''
        itemsTracks= [] # une liste
        itemtampon = xbmcgui.ListItem()
        for chaine in lachainedesItemsTracks:
            xbmc.log('detail album 1 item : ' + str(chaine), xbmc.LOGNOTICE)
            try:
                clef, valeur = chaine.split(':', 1)
            except ValueError:
                # probably there are some ':' in the chaine (lyrics or information around the title)
                # so we go on anyway
                pass

            if clef == 'id':

                if secondEtsuivant:
                    itemtampon.setLabel(indice + ' - ' + titre + ' - ' + year + ' : ' + duree + ' .')
                    itemtampon.setProperty('album_id' , album_id)
                    itemtampon.setProperty('artist_id' , artist_id)
                    itemsTracks.append(itemtampon)
                    itemtampon = xbmcgui.ListItem()
                    index = index + 1
                    xbmc.log( 'Ajout de l item dans listItem tampon' + titre + ' ' + itemtampon.getProperty('track_id'), xbmc.LOGNOTICE)

                itemtampon.setProperty('track_id', valeur)
                secondEtsuivant = True

            elif clef == 'title':
                titre = valeur
                #itemtampon.setLabel(valeur)

            elif clef == 'duration':
                duree = outils.getInHMS(valeur)

            elif clef == 'artwork_track_id':
                hascode_artwork = valeur
                completeNameofFile = self.get_artwork(hashcode_artwork=hascode_artwork)
                #itemtampon.setArt({'thumb': completeNameofFile})
                itemtampon.setProperty('image' , completeNameofFile)

            elif clef == 'tracknum':
                itemtampon.setProperty(clef, valeur)
                indice = valeur

            elif clef == 'year':
                itemtampon.setProperty(clef, valeur)
                year = valeur
            else:
                # not sure that we have to keep other value
                # for now we keep them but todo pass them
                itemtampon.setProperty(clef, valeur)

        # once exit the loop 'for' , fill the list with the last itemtampon :
        itemtampon.setProperty('album_id' , album_id)
        itemtampon.setProperty('artist_id' , artist_id)
        itemtampon.setLabel(indice + ' - ' + titre + ' - ' + year + ' : ' + duree + ' .')
        itemsTracks.append(itemtampon)
        xbmc.log( 'Ajout de l item dans listItem tampon ' + titre + ' ' + itemtampon.getProperty('track_id'), xbmc.LOGNOTICE)

        #sort the itemsTracks list by tracknum todo test this function or similar
        #sorted(itemsTracks, key=lambda tracknum: tracknum[1])   # sort by n° track not always true

        for item in itemsTracks:
            xbmc.log('ajout de item trackss dans menu detailAlbum  : ' + item.getLabel() , xbmc.LOGNOTICE)
            self.listMenu_detailAlbums.addItem(item)
    # End of funcion f_detailAlbums

    def f_listeTracks(self, menudeprovenance):
        
        if menudeprovenance ==  'listMenu_detailAlbums' :
            labelajouer = self.listMenu_detailAlbums.getListItem(self.listMenu_detailAlbums.getSelectedPosition()).getLabel()
            #cmd = self.command
            #cmd = self.listMenu_ItemRadios.getListItem( self.listMenu_ItemRadios.getSelectedPosition()).getProperty('cmd')
            #cmd ='picks' ,  ....Radio, shoutcast ...
            # cmd comes from listMenu_1 it is not an error
            tracknum = self.listMenu_detailAlbums.getListItem(
                self.listMenu_detailAlbums.getSelectedPosition()).getProperty('tracknum')
            track_id = self.listMenu_detailAlbums.getListItem(
                self.listMenu_detailAlbums.getSelectedPosition()).getProperty('track_id')
            album_id = self.listMenu_detailAlbums.getListItem(
                self.listMenu_detailAlbums.getSelectedPosition()).getProperty('album_id')
            artist_id = self.listMenu_detailAlbums.getListItem(
                self.listMenu_detailAlbums.getSelectedPosition()).getProperty('artist_id')

            xbmc.log('launch to play : ' + labelajouer + ' playlistcontrol cmd:load track_id:' + track_id , xbmc.LOGNOTICE  )


            choix = xbmcgui.Dialog().select(heading= labelajouer, list= ['Play Song now', \
                                                                         'Play Album now ' ,\
                                                                         'Play Song after the current song' , \
                                                                         'Add Song  to Playlist' , \
                                                                         'More Info'])

            if choix == 0:
                # exemple : playlistcontrol cmd:load album_id:1683
                requete = self.playerid + ' playlistcontrol cmd:load track_id:' + str(track_id)

            elif choix == 1:
                requete = self.playerid + ' playlistcontrol cmd:load album_id:' + str(album_id)

            elif choix == 2:
                requete = self.playerid + ' playlistcontrol cmd:insert track_id:' + str(track_id)

            elif choix == 3:
                requete = self.playerid + ' playlistcontrol cmd:add track_id:' + str(track_id)

            if not choix < 0 and not choix > 3 :
                xbmc.log('requete : ' + requete , xbmc.LOGNOTICE  )

                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()


                # now it is going to play
                requetePlay = self.playerid + ' playlist play'
                self.InterfaceCLI.sendtoCLISomething(requetePlay)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                del reponse
                # then stay on the screen and update duration and progress listmenu
                self.update_current_track_playing()

            elif choix == 4:
                # need more stuff to dig songinfo
                requete = self.playerid + ' songinfo 0 100 track_id:' + str(track_id)
                self.InterfaceCLI.sendtoCLISomething(requete)
                reponse = self.InterfaceCLI.receptionReponseEtDecodage()
                try:
                    listesonginfo = reponse.split('|')
                except ValueError:
                    self.functionNotYetImplemented()

                textInfo = ''
                for field in listesonginfo:

                    textInfo = textInfo +  field + '\r\n'

                dialogSongInfo = xbmcgui.Dialog()
                dialogSongInfo.textviewer('Song Info : ' + labelajouer , textInfo )

            else:
                # cancel asked
                pass
    # End of function f_listeTracks

    def f_detailItemPlaylist(self):
        # todo rewrite function to have a nice personnal textbox in a frame
        # with selected item

        labelajouer = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getLabel()
        track_id = self.listMenu_playlist.getListItem(
                self.listMenu_playlist.getSelectedPosition()).getProperty('tracked_id')
        self.connectInterface()
        self.get_playerid()
        self.subscribe = Ecoute.Souscription(self.InterfaceCLI, self.playerid)
        self.subscribe.resiliersouscription()
        self.InterfaceCLI.viderLeBuffer()
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
    def update_current_track_playing(self):

        self.subscribe = Souscription(self.InterfaceCLI, self.playerid )
        self.subscribe.subscription()
        # todo Q : comment faire la gestion de l'arret de la boucle de souscription ?
        #      A : fonction resiliersouscription()

        time.sleep(0.5)


        timeoutdeRecherchedesPlayers = time.time() + 60 * 20  # todo toutes les 20 minutes nous rechercherons les players
        timeEntreeDansLaBoucle = time.time()
        compteur = 1
        titreenlecture = ''
        self.breakBoucle_A = False
        self.Abonnement.set()
        while self.Abonnement.is_set():
            self.breakBoucle_A = False
            if xbmc.Monitor().waitForAbort(0.5):
                self.breakBoucle_A = True
                self.Abonnement.clear()
                break
            timeoutdeTestdelaBoucle = time.time() + 60 * 10  # 10 minutes from now -for testing
            while (self.breakBoucle_A == False):  # Boucle A principale de Subscribe ?same  as 'not self.breakBoucle_A'?

                if time.time() > timeoutdeTestdelaBoucle:
                    xbmc.log('Timeout : break A  ', xbmc.LOGNOTICE)
                    self.breakBoucle_A = True

                if xbmc.Monitor().waitForAbort(0.5):
                    self.breakBoucle_A = True
                    self.Abonnement.clear()

                # Todo : analyse du bloc
                recupropre = self.InterfaceCLI.receptionReponseEtDecodage()

                if 'subscribe:-' in recupropre:  # fin souscription the resiliersouscription is send by FramePlaying or
                    # else diplaying
                    # the FramePlaying  exits - function quit()
                    self.breakBoucle_A = True  # must exit the loop A but doesn't exist here
                    self.Abonnement.clear()  # must exit the main loop
                    break

                listeB = recupropre.split('subscribe:' + TIME_OF_LOOP_SUBSCRIBE + '|')  # on élimine le début de la trame
                # attention doit correpondre à
                # la même valeur de subscribe dans Ecoute.py

                try:
                    textC = listeB[1]  # on conserve la deuximème trame après suscribe...
                except IndexError:
                    break

                # mise à jour de la position de l'item dans le menu liste
                indexdecurrentTitle = textC.find('cur_index:')
                indexFincurrentTitle = textC.find('|', indexdecurrentTitle)
                # xbmc.log('index debut : ' + str(indexdecurrentTitle) + ' fin : ' + str(indexFincurrentTitle), xbmc.LOGDEBUG)
                playlist_current_index_title = textC[indexdecurrentTitle + 10: indexFincurrentTitle]
                xbmc.log('current_index_title :' + playlist_current_index_title, xbmc.LOGNOTICE)

                self.listMenu_detailAlbums.selectItem(int(playlist_current_index_title))

                listeRetour = textC.split('|')  # on obtient une liste des items
                dico = dict()  # pour chaque élement de la liste sous la forme <val1>:<val2>

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
                except KeyError:
                    continue

                try:
                    self.labelduree_jouee.setLabel(label=outils.getInHMS(dico['time']))
                except KeyError:
                    continue

                try:
                    self.labelduree_fin.setLabel(label=outils.getInHMS(dico['duration']))
                except KeyError:
                    self.labelduree_fin.setLabel(label=outils.getInHMS(0.0))

                if not dico['title'] == titreenlecture:

                    try:
                        self.title_label.setLabel(label='[B]' + dico['current_title'] + '[/B]')
                    except KeyError:
                        self.title_label.setLabel(label='')
                        pass
                    '''
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
                    '''
                    #self.update_coverbox(self.lmsip, self.lmswebport, self.playerid, compteur)

                # log pour voir
                compteur += 1
                timedutour = time.time()
                tempsparcouru = timedutour - timeEntreeDansLaBoucle
                xbmc.log(str(compteur) + ' tour de boucle : ' + str(tempsparcouru), xbmc.LOGDEBUG)
            # fin de la boucle A : sortie de subscribe
        # fin boucle while
        xbmc.log('End of Boucle in Update_curent_track in FrameMyMusic', xbmc.LOGNOTICE)
        self.subscribe.resiliersouscription()
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        xbmc.log('Send resiliersouscription in A update_current_track in FrameMyMusic', xbmc.LOGNOTICE)
        self.InterfaceCLI.viderLeBuffer()
        xbmc.log('End of fonction update_current_track_is_playing in FrameMyMusic, Bye', xbmc.LOGNOTICE)
    # fin fonction update_current_track_is_playing

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
