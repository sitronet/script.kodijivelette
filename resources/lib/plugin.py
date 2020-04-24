#!/usr/bin/env python
# -*- coding: utf-8 -*-

global Kodi
Kodi = True

global savepath
#savepath = '/tmp/' # savepath = 'special://temp'       # doesn't work on libreelec , why ?

if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct
    savepath = xbmc.translatePath('special://temp')

    ADDON_ID = 'script.kodijivelette'
    ADDON = xbmcaddon.Addon()
    ADDONID = ADDON.getAddonInfo('id')
    ADDONNAME = ADDON.getAddonInfo('name')
    ADDONVERSION = ADDON.getAddonInfo('version')

    DEBUG_LEVEL = xbmc.LOGDEBUG

    from resources.lib.outils import debug
    from resources.lib import frameMusicFolder
    from resources.lib import frameList
    from resources.lib import frameMyMusicAllArtists
    from resources.lib import frameMyMusicAlbums
    from resources.lib import frameMenuFavorites
    from resources.lib import connexionClient, outils

import urllib
import os
import sys
import time


ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))
ARTWORK_SLIM = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'Slimserver'))

TAGS = 'aCdejJKlstuwxy'

class Plugin_Generique():

    def __init__(self, parent):

        # todo : replace parent by the functions to initialize
        self.origine = parent

        #self.origine.InterfaceCLI.viderLeBuffer()

        self.get_ident_server()
        self.get_playerid()
        self.connectInterface()

        self.InterfaceCLI.viderLeBuffer()

        self.image_dir = ARTWORK
        self.image_slim = ARTWORK_SLIM

        self.image_folder = self.image_slim + '/icon_folder.png'
        self.image_musique = self.image_dir + '/music.png'


    def le_menu_branche(self, plugin):
        '''
        remplit le menu branche
        paramètre plugin should be : 'radios' , 'myapps', 'favorites' ...to try
        '''

        xbmc.log(' entrée dans le_menus_Branche_des_plugins ', xbmc.LOGNOTICE)
        self.origine.listMenu_Branches.reset()
        self.origine.listMenu_Branches.setVisible(True)
        self.origine.InterfaceCLI.sendtoCLISomething( plugin + ' 0 count')
        reponse = self.origine.InterfaceCLI.receptionReponseEtDecodage()

        # if the loop subscribre is always active
        while 'subscribe:' in reponse:
            reponse = self.origine.InterfaceCLI.receptionReponseEtDecodage()
        # or reponse contains 'plugin'

        nbre_a_traiter = reponse.split('count:')
        try:
            nombreD_items_a_traiter = nbre_a_traiter[1]  # on conserve la deuximème trame après 'count:' soit le nombre
            xbmc.log('nbre d items du plugin : ' + nombreD_items_a_traiter, xbmc.LOGNOTICE)
        except IndexError:
            # skip to end
            outils.functionNotYetImplemented()
            return

        self.origine.InterfaceCLI.sendtoCLISomething(plugin + ' 0 ' + nombreD_items_a_traiter)
        reponse_propre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
        lesItemsduPlugin = reponse_propre.split('count:' + nombreD_items_a_traiter + '|')
        '''
        exemple de trame :
        radios|0|11|sort:weight|count:11|
        icon:/plugins/TuneIn/html/images/radiopresets.png|cmd:presets|weight:5|name:My Presets|type:xmlbrowser|
        [...]
        icon:/plugins/TuneIn/html/images/podcasts.png|cmd:podcast|weight:70|name:Podcasts|type:xmlbrowser|
        icon:/plugins/TuneIn/html/images/radiosearch.png|cmd:search|weight:110|name:Search|type:xmlbrowser_search
        
        exemple de trame apps :
        apps|0|15|sort:weight|count:15|
        icon:plugins/RadioParadise/html/icon.png|cmd:radioparadise|weight:1|name:Radio Paradise|type:xmlbrowser|
        icon:plugins/RhapsodyDirect/html/images/icon.png|cmd:rhapsodydirect|weight:20|name:Napster|type:xmlbrowser|
        [...]
        icon:plugins/Live365/html/images/icon.png|cmd:live365|weight:1000|name:Live365|type:xmlbrowser|
        icon:plugins/Flickr/html/images/icon.png|cmd:flickr|weight:1000|name:Flickr|type:xmlbrowser

        exemple de trame favorites :
        favorites|items|0|8|title:Favorites|
        id:0|name:Sur mysqueezebox.com|isaudio:0|hasitems:1|
        id:1|name:Dogs of War|type:audio|isaudio:1|hasitems:0|
        [...]
        id:6|name:FIP 96.5 (Musique Française)|type:audio|isaudio:1|hasitems:0|
        id:7|name:Dirty Electrofunk Mash Up Vol:2|type:playlist|isaudio:1|hasitems:1|
        count:8

        '''
        # todo : retravailler le cmd problème similaire au title dans feuilles
        listeBrutedesItemsduPlugin = lesItemsduPlugin[1].split('|type:xmlbrowser|')
        self.listepropredesItemsduPlugin = []
        dictionnaireUnPlugin = dict()
        for unItemBrut in listeBrutedesItemsduPlugin:
            try:
                listeTempUnPlugin = unItemBrut.split('|')
            except IndexError:
                outils.functionNotYetImplemented()
                return
            for unchamps in listeTempUnPlugin:
                key, value = unchamps.split(':', 1)
                dictionnaireUnPlugin[key] = value
            self.listepropredesItemsduPlugin.append(dictionnaireUnPlugin.copy()) # liste de dictionnaires

        for unItem in self.listepropredesItemsduPlugin:

            completeNameofFile = self.get_icon(index=unItem.get('name'), urlicone=unItem.get('icon'))

            itemdeListe = xbmcgui.ListItem()
            itemdeListe.setLabel(unItem.get('name'))
            itemdeListe.setArt({'thumb': completeNameofFile})
            self.origine.listMenu_Branches.addItem(itemdeListe)


        self.origine.setFocus(self.origine.listMenu_Branches)
        return self.listepropredesItemsduPlugin #   c'est une liste, chaque entrée de la liste est un dictionnaire

    # fin fonction le_menu_branche , class Plugin_Generique


    def le_menu_feuille(self, numeroItemSelectionBranche):
        '''
        remplit le menu feuille

        plugin similar to apps here
        '''

        xbmc.log(' entrée dans le_menu_feuille_des_plugins', xbmc.LOGNOTICE)
        self.origine.listMenu_Feuilles.reset()
        self.origine.listMenu_Feuilles.setVisible(True)

        dictionnaireSelectioned = self.origine.liste_du_menu_branche_des_plugins[numeroItemSelectionBranche]

        plugin = dictionnaireSelectioned['cmd']
        self.origine.InterfaceCLI.sendtoCLISomething(plugin + ' items ' + ' count ')
        nbre_a_traiter = self.origine.InterfaceCLI.receptionReponseEtDecodage().split('count:')
        try:
            nombreDItemsApplication = nbre_a_traiter.pop()
        except IndexError:
            outils.functionNotYetImplemented()
            return
        # TODO : if count greater than X : cut the request in pièce not more 5 or 8
        start = '0'
        self.origine.InterfaceCLI.sendtoCLISomething(plugin + ' items ' +  start + '  '  + nombreDItemsApplication)
        reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
        lesItemsApps = reponsepropre.split('items|' + start + '|' + nombreDItemsApplication + '|' ) # todo attention si le nombre est 1
        try:
            lachainedesItemsApps = lesItemsApps[1].split('|')
        except IndexError:
            outils.functionNotYetImplemented()
            return
        listedesdictionnairedesItemsApps = [{} for _ in range(int(nombreDItemsApplication)  )]  # magic word
        # for now listedesdictionnairedesItemsApps is : [ {}, {}, {}, {}, {}, {}, {}, {} ]

        index = 0
        for chaine in lachainedesItemsApps:
            try:
                clef, valeur = chaine.split(':', 1)
            except ValueError:
                outils.functionNotYetImplemented()

            if clef == 'title':
                pass

            elif clef == 'count':
                pass

            else:
                listedesdictionnairedesItemsApps[index][clef] = valeur

            if clef == 'hasitems':
                index = index + 1

        listedesItemsApps = listedesdictionnairedesItemsApps

        dictionnaireUnItemApp = dict()

        for dictionnairedUnItemApp in listedesItemsApps:

            itemdeListe = xbmcgui.ListItem()
            itemdeListe.setLabel(dictionnairedUnItemApp.get('name'))
            itemdeListe.setProperty( 'cmd' , plugin )
            itemdeListe.setProperty( 'id' , dictionnairedUnItemApp.get('id'))
            itemdeListe.setProperty( 'isaudio' , dictionnairedUnItemApp.get('isaudio'))
            itemdeListe.setProperty( 'type' , dictionnairedUnItemApp.get('type'))
            itemdeListe.setProperty('hasitems' , dictionnairedUnItemApp.get('hasitems'))

            if dictionnairedUnItemApp.get('icon') or dictionnairedUnItemApp.get('image'):

                if dictionnairedUnItemApp.get('icon'):
                    ulricone = dictionnairedUnItemApp.get('icon')
                elif dictionnairedUnItemApp.get('image'):
                    ulricone = dictionnairedUnItemApp.get('image')
                if plugin == 'radios':
                    completeNameofFile = self.get_icon(index=str(dictionnairedUnItemApp.get('name')), urlicone=ulricone)
                else:
                    completeNameofFile = self.get_icon(index=str(dictionnairedUnItemApp.get('name')), urlicone=ulricone)


                itemdeListe.setArt({'thumb': completeNameofFile})
                self.command = dictionnairedUnItemApp.get('cmd')
            self.origine.listMenu_Feuilles.addItem(itemdeListe)
        self.origine.setFocus(self.origine.listMenu_Feuilles)
        # fin fonction le_menu_feuille, class Plugin_Generique

    def le_menu_fleurs(self, numeroItemSelectionFeuille):
        ''' à redéfinir avec param : menu entrée d'où on vient'''
        xbmc.log(' entrée dans le_menu_fleurs_des_plugins', xbmc.LOGNOTICE)

        start = '0'
        # l'un ou l'autre ?
        itemdelisteOrigine = self.origine.listMenu_Feuilles.getListItem(numeroItemSelectionFeuille)
        labeldetete = itemdelisteOrigine.getLabel()
        self.command = itemdelisteOrigine.getProperty('cmd')
        cmd = itemdelisteOrigine.getProperty('cmd')
        item_id = itemdelisteOrigine.getProperty('id')
        xbmc.log( 'menu fleur , cmd & id ' + cmd + ' ' + item_id , xbmc.LOGNOTICE)

        # creation  d'une nouvelle fenêtre
        #self.longListing = frameList.ViewListPlugin(labeldetete)
        self.longListing = frameList.ViewListPlugin()
        #self.longListing.show()
        #self.longListing.doModal()

        #for indice in (1,2, 3 ,4):
        #    self.longListing.ArrayOfMenu[indice].reset()
        #self.longListing.ArrayOfMenu[1].reset()
        self.longListing.listMenu_1.reset()
        #self.origine.listMenu_Fleur.reset()

        if itemdelisteOrigine.getProperty('hasitems') == '1':

            self.origine.InterfaceCLI.sendtoCLISomething(cmd + ' items  item_id:' + item_id +  ' count ')
            reponse =  self.origine.InterfaceCLI.receptionReponseEtDecodage()
            # exemple reponse  receptionReponseEtDecodage() radio staff picks :
            # 00:04:20:17:1c:44|picks|items|0|count|item_id:547a1ec5.0|title:Andy's Picks|count:3
            texte_en_liste_a_traiter = reponse.split('|count:')
            xbmc.log('texte_a_traiter : ' +  str(texte_en_liste_a_traiter) , xbmc.LOGNOTICE )
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
            try:
                texte_a_traiter_titre = texte_en_liste_a_traiter.pop()
                texte_en_liste_a_traiter_titre = texte_a_traiter_titre.split('title:')
                xbmc.log('texte_a_traiter titre: ' +  str(texte_en_liste_a_traiter_titre) , xbmc.LOGNOTICE )
            except IndexError:
                pass
            # exemple :  ['00:04:20:17:1c:44|picks|items|0|count|item_id:c4bca76a.0|', "Andy's Picks"]
            try:
                title = texte_en_liste_a_traiter_titre.pop()
            except IndexError:
                outils.functionNotYetImplemented()

            #if nombreDItemsapplications > 9:
            # turn 8 by 8 (step 8)
            #self.longListing.title_label.setLabel(title)
            self.origine.list_item_fleur_label.setLabel(title)
            start = 0
            step = 8
            indicedesmenus = 1 # max = 4
            nbre_recolted = 0
            nbre_restant_a_recolter = int(nombreDItemsapplications)
            while nbre_recolted  < int(nombreDItemsapplications):
                #indicedesmenus = indicedesmenus + 1 # todo : à revoir pour incrémenter jusqu'à 4 listmenu
                if nbre_restant_a_recolter > step:
                    self.origine.InterfaceCLI.sendtoCLISomething( cmd + ' items ' +  str(start) + '  '  + \
                                             str(step) + ' item_id:' +  str(item_id) )
                    reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
                    xbmc.log('Les Fleurs unefoispropre : ' + str(reponsepropre) , xbmc.LOGNOTICE)
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
                    # Todo : for radios by language the answer is not the same so bug

                    lesItemsFleurs = reponsepropre.split('items|' + str(start) + '|' + str(step) + '|' )
                    xbmc.log('ligne 269 : ' + 'items|' + str(start) + '|' + str(step) + '|'  , xbmc.LOGNOTICE)
                    xbmc.log('ligne 270 : ' + str(lesItemsFleurs) , xbmc.LOGNOTICE)
                    nbre_recolted = nbre_recolted + step
                    nbre_restant_a_recolter = nbre_restant_a_recolter - step
                    start = start + step

                else: # moins d'items que le step
                    requete_construite = cmd + ' items ' +  str(start) + ' '  + str(nbre_restant_a_recolter) + ' item_id:' +  str(item_id)
                    self.origine.InterfaceCLI.sendtoCLISomething( requete_construite )
                    reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
                    xbmc.log('Les Fleurs unefoispropre : ' + str(reponsepropre) , xbmc.LOGNOTICE)
                    '''
                    exemple : 00:04:20:17:1c:44|picks|items|0|3|item_id:63d6bace.0|title:Andy's Picks|
                    id:63d6bace.0.0|name:Sofaspace Ambient Radio (Vorbis)|type:audio|isaudio:1|hasitems:0|
                    id:63d6bace.0.1|name:SomaFM - Groove Salad|type:audio|isaudio:1|hasitems:0|
                    id:63d6bace.0.2|name:Lounging Sound|type:audio|isaudio:1|hasitems:0|
                    count:3
                    '''
                    lesItemsFleurs = reponsepropre.split('items|' + str(start) + '|' + str(nbre_restant_a_recolter)  + '|' )
                    nbre_recolted = nbre_recolted + nbre_restant_a_recolter

                xbmc.log('la récolte a été bonne de  : ' + str(nbre_recolted) , xbmc.LOGNOTICE)

                #trim the count and trim the title
                try:
                    lesItemsFleurs_text = lesItemsFleurs[1]
                except IndexError:
                    outils.functionNotYetImplemented()

                    return
                try:
                    xbmc.log('lesItemsFleurs_text : ' + lesItemsFleurs_text, xbmc.LOGDEBUG )
                    index_du_count = lesItemsFleurs_text.find('|count:')
                    xbmc.log('index count : ' + str(index_du_count), xbmc.LOGDEBUG )
                    index_du_titre = lesItemsFleurs_text.find('title:')
                    xbmc.log('index titre : ' + str(index_du_titre), xbmc.LOGDEBUG )
                    index_du_fin_de_titre = lesItemsFleurs_text.find('|', index_du_titre)
                    xbmc.log('index fin du  titre : ' + str(index_du_fin_de_titre), xbmc.LOGDEBUG )

                    lesItemsFleursNormalised = lesItemsFleurs_text[index_du_fin_de_titre + 1 : index_du_count]
                    xbmc.log('lesItemsFleursNormalised : ' + lesItemsFleursNormalised, xbmc.LOGNOTICE )
                except:
                    outils.functionNotYetImplemented()

                    return

                '''
                exemple : 
                |id:3a7d1dbb.0.0|name:Sofaspace Ambient Radio (Vorbis)|type:audio|isaudio:1|hasitems:0|
                id:3a7d1dbb.0.1|name:SomaFM - Groove Salad|type:audio|isaudio:1|hasitems:0|
                id:3a7d1dbb.0.2|name:Lounging Sound|type:audio|isaudio:1|hasitems:0
                '''

                try:
                    lachainedesItemsFleurs = lesItemsFleursNormalised.split('|')#
                    xbmc.log('ligne 317 : ' + str(lachainedesItemsFleurs) , xbmc.LOGNOTICE)
                except:
                    xbmc.log('functionNotYetImplemented Ligne 323', xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()

                    return

                index = 0
                itemsFleur= [] # une liste
                itemtampon = xbmcgui.ListItem()
                #itemsFleur.append(itemtampon)
                for chaine in lachainedesItemsFleurs:
                    xbmc.log('Plugin::Fleur -> chaine d 1 item : ' + str(chaine), xbmc.LOGDEBUG)
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
                    xbmc.log('ajout de item dans menu frameList::listMenu_1 : ' + item.getLabel() , xbmc.LOGNOTICE)
                    #self.longListing.ArrayOfMenu[indicedesmenus].addItem(item)
                    self.longListing.listMenu_1.addItem(item)
                    #self.origine.listMenu_Fleur.addItem(item)

            self.longListing.doModal()
            #xbmc.Monitor().waitForAbort()
            del self.longListing

        # fin fonction fin fonction le_menu_fleurs, class Plugin_Generique

    def get_icon(self, index, urlicone):
        '''
        fetch the image or icon from server or somewhere in tne net
        and store it in a temporay directory .
        ie /tmp/ on unix or
        special://tmp
        '''
        filename = 'icon.image_' + str(index) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)
        xbmc.log('filename icon : ' + str(completeNameofFile), xbmc.LOGDEBUG)

        if 'http' in urlicone:
            urltoopen = urlicone
        else:
            if urlicone.startswith('/'):
                xbmc.log('url icone avec /: ' + urlicone ,xbmc.LOGDEBUG )
            #urltoopen = 'http://' + self.origine.rechercheduserveur.LMSCLIip + ':' +
            #               self.origine.rechercheduserveur.LMSwebport + '/' + urlicone
                urltoopen = 'http://' + self.origine.rechercheduserveur.LMSCLIip + ':' \
                            + self.origine.rechercheduserveur.LMSwebport + urlicone
            else:
                xbmc.log('url icone sans /: ' + urlicone ,xbmc.LOGDEBUG )
                urltoopen = 'http://' + self.origine.rechercheduserveur.LMSCLIip + ':' \
                            + self.origine.rechercheduserveur.LMSwebport + '/' + urlicone
        try:
            urllib.urlretrieve(urltoopen, completeNameofFile)
        except IOError:
            outils.functionNotYetImplemented()

        xbmc.log('nom du fichier image : ' + completeNameofFile , xbmc.LOGNOTICE)
        return completeNameofFile
        # fin fonction fin fonction get_icon, class Plugin_Generique

    def get_artwork(self, hashcode_artwork):
        # http://<server>:<port>/music/<track_id>/cover.jpg
        filename = 'icon.image_' + str(hashcode_artwork) + '.tmp'
        completeNameofFile = os.path.join(savepath, filename)

        urlimage = 'http://' + self.lmsip + ':' + self.lmswebport + '/music/' + str(hashcode_artwork) + '/cover.jpg'
        debug('urlToGet : ' + str(urlimage), xbmc.LOGNOTICE)
        try:
            urllib.urlretrieve(urlimage, completeNameofFile)
        except IOError:
            debug('erreur download artwork', xbmc.LOGNOTICE)
            outils.functionNotYetImplemented()
        xbmc.log('nom du fichier image in get_artwork : ' + completeNameofFile, xbmc.LOGNOTICE)
        return completeNameofFile


    def connectInterface(self):
        self.InterfaceCLI = connexionClient.InterfaceCLIduLMS()

    def get_playerid(self):
        self.Players = outils.WhatAreThePlayers()
        self.playerid = self.Players.get_unplayeractif()

    def get_ident_server(self):
        self.Server = outils.WhereIsTheLMSServer()
        self.nomserver = self.Server.LMSnom
        self.lmsip = self.Server.LMSCLIip
        self.lmswebport = self.Server.LMSwebport

    # fin class Plugin_Generique , father

class Plugin_Favorites(Plugin_Generique):
    '''
    extends for Favorites as it seems that count deep differs

    '''
    #todo

    def le_menu_branche(self, plugin='favorites'):
        '''
        remplit le menu branche dérivé de générique
        paramètre plugin should be here 'favorites' ...to try
        main diff :   the request to count is not the same
        todo : peupler le menu_fleur de Framelist au lieu ddu menu branches
        '''

        xbmc.log(' entrée dans le_menus_Branche_du_Plugin Favorites', xbmc.LOGNOTICE)
        self.origine.listMenu_Branches.reset()

        # creation  d'une nouvelle fenêtre
        #self.longListing = frameList.ViewListPlugin(plugin)
        #self.longListing.show()
        # self.longListing.doModal()
        # remplacé pour test  (Todo)
        self.longListing = frameMenuFavorites.FavoritesMenu()
        self.longListing.show()

        # for indice in (1,2, 3 ,4):
        #    self.longListing.ArrayOfMenu[indice].reset()
        #self.longListing.ArrayOfMenu[1].reset()
        # self.origine.listMenu_Fleur.reset()
        self.longListing.listMenu_1.reset()

        self.origine.InterfaceCLI.sendtoCLISomething( plugin + ' items')
        nbre_a_traiter = self.origine.InterfaceCLI.receptionReponseEtDecodage().split('count:')
        try:
            nombreD_items_a_traiter = nbre_a_traiter[1]  # on conserve la deuximème trame après suscribe...
            xbmc.log('nbre d items du plugin : ' + nombreD_items_a_traiter, xbmc.LOGNOTICE)
        except IndexError:
            # skip to end
            outils.functionNotYetImplemented()
            return
        '''
        exemple favorites items  :
        favorites|items|0|8|title:Favorites|
        id:0|name:Sur mysqueezebox.com|isaudio:0|hasitems:1|
        id:1|name:Dogs of War|type:audio|isaudio:1|hasitems:0|
        id:2|name:France Inter 89.7 (Émissions-débats France)|type:audio|isaudio:1|hasitems:0|
        id:3|name:Radio Paradise|type:audio|isaudio:1|hasitems:0|
        id:4|name:FIP Bordeaux 96.7 (Musique Française)|type:audio|isaudio:1|hasitems:0|
        id:5|name:Radio Paradise AAC 320|type:audio|isaudio:1|hasitems:0|
        id:6|name:FIP 96.5 (Musique Française)|type:audio|isaudio:1|hasitems:0|
        id:7|name:Dirty Electrofunk Mash Up Vol:2|type:playlist|isaudio:1|hasitems:1|
        count:8
        '''
        start = '0'
        self.origine.InterfaceCLI.sendtoCLISomething(plugin + ' items 0 ' + nombreD_items_a_traiter)
        reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
        lesItemsApps = reponsepropre.split(
            'items|' + start + '|' + nombreD_items_a_traiter+ '|')  # todo attention si le nombre est 1
        try:
            lachainedesItemsApps = lesItemsApps[1].split('|')
        except IndexError:
            outils.functionNotYetImplemented()

            return
        listedesdictionnairedesItemsApps = [{} for _ in range(int(nombreD_items_a_traiter))]  # magic word
        # for now listedesdictionnairedesItemsApps is : [ {}, {}, {}, {}, {}, {}, {}, {} ]

        index = 0
        for chaine in lachainedesItemsApps:
            try:
                clef, valeur = chaine.split(':', 1)
            except ValueError:
                outils.functionNotYetImplemented()


            if clef == 'title':
                pass

            elif clef == 'count':
                pass

            else:
                listedesdictionnairedesItemsApps[index][clef] = valeur

            if clef == 'hasitems':
                index = index + 1

        listedesItemsFavorites = listedesdictionnairedesItemsApps

        dictionnaireUnItemApp = dict()

        for dictionnairedUnItemApp in listedesItemsFavorites:

            itemdeListe = xbmcgui.ListItem()
            itemdeListe.setLabel(dictionnairedUnItemApp.get('name'))
            itemdeListe.setProperty('cmd', plugin)
            itemdeListe.setProperty('id', dictionnairedUnItemApp.get('id'))
            itemdeListe.setProperty('isaudio', dictionnairedUnItemApp.get('isaudio'))
            itemdeListe.setProperty('type', dictionnairedUnItemApp.get('type'))
            itemdeListe.setProperty('hasitems', dictionnairedUnItemApp.get('hasitems'))

            if dictionnairedUnItemApp.get('icon') or dictionnairedUnItemApp.get('image'):
                if dictionnairedUnItemApp.get('icon'):
                    ulricone = dictionnairedUnItemApp.get('icon')
                elif dictionnairedUnItemApp.get('image'):
                    ulricone = dictionnairedUnItemApp.get('image')

                completeNameofFile = self.get_icon(index=dictionnairedUnItemApp.get('id'), urlicone=ulricone)

                itemdeListe.setArt({'thumb': completeNameofFile})
                itemdeListe.setProperty('image', completeNameofFile)

                self.command = dictionnairedUnItemApp.get('cmd')
            self.longListing.listMenu_1.addItem(itemdeListe)

        self.longListing.listMenu_1.setVisible(True)
        xbmc.log(' Sortie de le_menu_branche_des_plugins Favorites', xbmc.LOGNOTICE)
        #return listedesItemsFavorites

        xbmc.Monitor().waitForAbort()
        del self.longListing
    # fin fonction fin fonction le_menu_branches, class Plugin_Favorites

    def le_menu_feuille(self, numeroItemSelectionBranche):

        '''
        Don't need as the list of favorites is opened in the frameList  by menu_branches

         le menu feuille des Favoris : joue directement si audio et n'a pas de suite

        plugin similar to apps here
        the diff are :

         if has no items to dig -> play the item
         else dig one more
        '''

        xbmc.log(' entrée dans le_menu_feuille_des_plugins Favoris', xbmc.LOGNOTICE)
        self.origine.listMenu_Feuilles.reset()


        dictionnaireSelectioned = self.origine.liste_du_menu_branche_des_plugins[numeroItemSelectionBranche]

        #cmd = dictionnaireSelectioned['cmd']
        cmd = 'favorites'
        labelajouer = dictionnaireSelectioned['name']
        item_id = dictionnaireSelectioned['id']

        
        if dictionnaireSelectioned['hasitems'] == 0 and dictionnaireSelectioned['type'] == 'audio':

            choix = xbmcgui.Dialog().select(labelajouer, ['Play', 'Play after the current song' ,  'Add to Playlist' ])
            if choix == 0:
                requete = cmd + ' playlist play item_id:' + str(item_id)
            elif choix == 1:
                requete = cmd + ' playlist insert item_id:' + str(item_id)
            elif choix == 2:
                requete = cmd + ' playlist add item_id:' + str(item_id)
            else:
                # not well coded
                pass

            self.connectInterface()

            self.InterfaceCLI.sendtoCLISomething(requete)
            reponse = self.InterfaceCLI.receptionReponseEtDecodage()
            del reponse

            # then launch now is playing framePlaying
            self.Abonnement.set() # need to renew subscribe after interupt
            self.jivelette = framePlaying.SlimIsPlaying()

            self.WindowPlaying = xbmcgui.getCurrentWindowId()
            xbmc.log('fenetre en cours n° : ' + str(self.WindowPlaying), xbmc.LOGNOTICE)

            # todo : test inversion show et doModal
            self.jivelette.show()

            self.get_playerid()
            self.get_ident_server()

            #time.sleep(0.5)
            self.update_now_is_playing()
            #self.update_now_is_playing()
            #self.jivelette.doModal()
            del self.jivelette

        else:
            # in case we have to dig one more time , it shouldn't happens
            outils.functionNotYetImplemented()


        # fin fonction le_menu_feuille, surcharge dans class Plugin_Favorites

class MyMusic(Plugin_Generique):
    '''
    plugin to ask the personnal music database on the LMS server
    there are many ways to put the songs by artist, by album, by genre or anything else.

    '''

    #def __init__(self, *args, **kwargs):

    #def __init__(self, parent):

        #super(MyMusic, self).__init__(parent) #ca marche pas ça : TypeError

        #self.origine = parent

        #self.get_playerid()
        #self.get_ident_server()
        #self.connectInterface()
        #self.InterfaceCLI.viderLeBuffer()

    def le_menu_feuille(self, numeroItemSelectionBranche, label_branche):
        '''
         (listMenu_Racine) item : My Music-> (listMenu_MyMusic) iem : All Artist -> (by menu_feuille : listMenu_Feuilles_all_artists)
         then by menu_fleur : frameList::list_menu_1

        remplit la liste selon la demande (numeroItemSelectionBranche = selection ie artists, albums ... )
        ['Album Artists', 'All Artists', 'Composers', 'Albums', 'Compilations', 'Genres', \
                                     'Years', 'New Music', 'Random Mix', 'Music Folder', 'Playlists', 'Search', \
                                     'Remote Music Librairies']

        For now function populate the list menu feuille in frameMenu of all artists (choice 1 )

        but it must do other like random music except if in a new plugin
        '''
        debug('entry in : ' + self.__class__.__name__  + ' ' +  sys._getframe().f_code.co_name , xbmc.LOGNOTICE)

        # todo : not necessary need, could be in the initial menu switch (self.origine)
        #if  numeroItemSelectionBranche == 2 or \
        #    numeroItemSelectionBranche == 4 or \
        #    numeroItemSelectionBranche == 5 or \
        #    numeroItemSelectionBranche == 6 or \
        #    numeroItemSelectionBranche == 7 or \
        #    numeroItemSelectionBranche == 10 or \
        #    numeroItemSelectionBranche == 11:
            
        #    outils.functionNotYetImplemented()

        if label_branche == 'Album Artists':
        #elif numeroItemSelectionBranche == 0 :  # liste ArtistAlbums
            debug(' entrée dans plugin.MyMusic.le_menu_feuille', xbmc.LOGNOTICE)
            if self.origine.ArtistAlbums_populated:
                return

            # the same processing as all albums excepted few change
            self.origine.InterfaceCLI.viderLeBuffer()
            self.origine.InterfaceCLI.sendtoCLISomething('info total albums ?')
            reponse = self.origine.InterfaceCLI.receptionReponseEtDecodage()
            try:
                nbre_a_traiter = reponse.split('|')
                nbre_total_albums = nbre_a_traiter.pop()
            except IndexError:
                debug('FNYI : recherche ArtistAlbum nbre_a_traiter plugin.py', xbmc.LOGNOTICE)
                outils.functionNotYetImplemented()
                return

            buddydialog = xbmcgui.DialogProgress()
            buddydialog.create('look after ' + nbre_total_albums + ' Albums')

            start = 0
            step = 800
            end = step
            nbre_recolted = 0
            nbre_a_recolter = int(nbre_total_albums)
            nbre_restant = nbre_a_recolter
            nbre_restant_a_recolter = nbre_restant
            nbre_pour_calculer_buddydialog = 0
            percent = 0
            buddydialog.update(percent)
            TAGSARTFLOW = 'ijl'
            while nbre_recolted < nbre_a_recolter:
                if nbre_restant_a_recolter > step:
                    requete = 'albums ' + str(start) + ' ' + str(end) + ' sort:artistalbum'
                    self.origine.InterfaceCLI.sendtoCLISomething(requete)
                    nbre_recolted = nbre_recolted + step
                    nbre_restant_a_recolter = nbre_restant_a_recolter - step  # = nbre_a_recolter - nbre_recolted
                    start = start + step
                    end = start + step
                else:  # reste  moins d'items que le step
                    requete= 'albums ' + str(start) + ' ' + str(nbre_a_recolter) + ' sort:artistalbum'
                    self.origine.InterfaceCLI.sendtoCLISomething(requete)
                    nbre_recolted = nbre_recolted + nbre_restant_a_recolter

                debug('la récolte a été bonne de  : ' + str(nbre_recolted), xbmc.LOGNOTICE)

                reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
                debug('Les albums unefoispropre : ' + str(reponsepropre), xbmc.LOGNOTICE)

                # if the buffer is truncated we need to colapse it
                while not ('count:' + str(nbre_total_albums)) in reponsepropre:
                    reponsepropre = reponsepropre + self.origine.InterfaceCLI.receptionReponseEtDecodage()

                # here we get a string with albums we need to analyse it
                # trim the tail count
                try:
                    lesItemsAlbums = reponsepropre.split('|count:')
                    xbmc.log('listetemp des Albums' + str(lesItemsAlbums), xbmc.LOGDEBUG)

                    lesItemsAlbums_text = lesItemsAlbums[0]
                except IndexError:
                    debug('FNYI : recherche ArtistAlbum lesItemsAlbums plugin.py', xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()
                    return
                # trim the head :
                try:

                    index_de_fin_de_artflow = lesItemsAlbums_text.find('sort:artistalbum|')
                    debug('index fin du artflow : ' + str(index_de_fin_de_artflow), xbmc.LOGNOTICE)
                    lesItemsAlbumsNormalised = lesItemsAlbums_text[index_de_fin_de_artflow :]
                    debug('les Items Albums Normalised : ' + lesItemsAlbumsNormalised, xbmc.LOGNOTICE)
                except:
                    debug('FNYI : recherche ArtistAlbum indexdefin artflow plugin.py', xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()
                    return

                # here we have a nice string of albums ' id:xxx|album:AAAA|id:yyy|album:BBBB etc...
                try:
                    lachainedesItemsAlbums = lesItemsAlbumsNormalised.split('|')  #
                    debug('chaine des items albums  : ' + str(lachainedesItemsAlbums), xbmc.LOGDEBUG)
                except:
                    debug('FNYI :  recherche artist Albums lachainedesItemsAlbums plugin.py', xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()
                    return

                itemtampon = xbmcgui.ListItem()  # prepare le menulist
                for chaine in lachainedesItemsAlbums:
                    # prepare update buddydialogprogress
                    nbre_pour_calculer_buddydialog = nbre_pour_calculer_buddydialog + 1
                    try:
                        clef, valeur = chaine.split(':', 1)
                    except ValueError:
                        # some time the field send by server is not good, there is a real space rather an encoded space
                        # exemple in my library : id:2806|artist:Bruno Mars | www.RNBxBeatz.com|
                        pass

                    if clef == 'id':
                        itemtampon.setProperty('album_id', str(valeur))

                    elif clef == 'album':
                        itemtampon.setLabel(valeur)
                        self.origine.listMenu_Feuilles_ArtistAlbums.addItem(itemtampon)
                        debug('Id item album : ' + str(itemtampon.getProperty('album_id')) + valeur, xbmc.LOGNOTICE)
                        itemtampon = xbmcgui.ListItem()

                percent = int(nbre_pour_calculer_buddydialog / int(nbre_a_recolter)) * 100
                buddydialog.update(percent)

            buddydialog.close()
            self.origine.ArtistAlbums_populated = True

        # end if lister ArtistAlbums

        elif label_branche == 'All Artists':
        #elif numeroItemSelectionBranche == 1: # liste 'all artists'
            xbmc.log(' entrée dans le menu all artists du_plugin MyMusic', xbmc.LOGNOTICE)
            if self.origine.all_Artists_populated:
                return

            self.origine.InterfaceCLI.viderLeBuffer()
            self.origine.InterfaceCLI.sendtoCLISomething('artists')
            nbre_a_traiter = self.origine.InterfaceCLI.receptionReponseEtDecodage().split('count:')
            try:
                nombreDItems = nbre_a_traiter.pop()
            except IndexError:
                outils.functionNotYetImplemented()
                return

            # calcul de la répartition sur 3 colonnes :

            nombreparcolonne , reste = divmod(int(nombreDItems), 3)

            # create a dialog view of the busy digging
            #buddydialog = xbmcgui.DialogProgressBG()

            buddydialog = xbmcgui.DialogProgress()
            buddydialog.create('dig out ' + nombreDItems + ' Artists' )

            start = 0
            step = 800
            end = step
            indicedesmenus = 1  # max = 3
            nbre_recolted = 0
            nbre_a_recolter = int(nombreDItems)
            nbre_restant_a_recolter = int(nombreDItems)
            nbre_pour_calculer_buddydialog = 0
            percent = 0
            buddydialog.update(percent)
            while nbre_recolted < nbre_a_recolter:
                # indicedesmenus = indicedesmenus + 1 # todo : à revoir pour incrémenter jusqu'à 4 listmenu
                if nbre_restant_a_recolter > step:
                    self.origine.InterfaceCLI.sendtoCLISomething('artists ' + str(start) + '  ' + str(end))
                    nbre_recolted = nbre_recolted + step
                    nbre_restant_a_recolter = nbre_restant_a_recolter - step # = nbre_a_recolter - nbre_recolted
                    start = start + step
                    end = start + step
                else:  #reste  moins d'items que le step
                    requete_construite = 'artists ' + str(start) + ' ' + str(nbre_a_recolter)
                    self.origine.InterfaceCLI.sendtoCLISomething(requete_construite)
                    nbre_recolted = nbre_recolted + nbre_restant_a_recolter

                xbmc.log('la récolte a été bonne de  : ' + str(nbre_recolted), xbmc.LOGNOTICE)

                reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
                xbmc.log('Les artists unefoispropre : ' + str(reponsepropre), xbmc.LOGDEBUG)

                # trim the count and trim the title
                try:
                    lesItemsArtists = reponsepropre.split('|count:')
                    xbmc.log('listetemp' + str(lesItemsArtists), xbmc.LOGDEBUG)

                    lesItemsArtists_text = lesItemsArtists[0]
                except IndexError:
                    outils.functionNotYetImplemented()

                    return

                try:
                    index_du_debut = lesItemsArtists_text.find('artists ' + str(start) + ' ' + str(step) + '|')
                    xbmc.log('index count : ' + str(index_du_debut), xbmc.LOGDEBUG)
                    index_du_fin_de_titre = lesItemsArtists_text.find('id',)
                    xbmc.log('index fin du  titre : ' + str(index_du_fin_de_titre), xbmc.LOGDEBUG)
                    lesItemsArtistsNormalised = lesItemsArtists_text[index_du_fin_de_titre : ]
                    xbmc.log('lesItemsArtistsNormalised : ' + lesItemsArtistsNormalised, xbmc.LOGDEBUG)
                except:
                    outils.functionNotYetImplemented()

                    return

                try:
                    lachainedesItemsArtists = lesItemsArtistsNormalised.split('|')  #
                    xbmc.log('plugin_mymusic , ligne xxx : ' + str(lachainedesItemsArtists), xbmc.LOGDEBUG)
                except:
                    xbmc.log('functionNotYetImplemented  plugin my_music Ligne xxx', xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()

                    return

                itemsArtist = []  # une liste
                itemtampon = xbmcgui.ListItem()

                for chaine in lachainedesItemsArtists:
                    nbre_pour_calculer_buddydialog = nbre_pour_calculer_buddydialog + 1

                    try:
                        clef, valeur = chaine.split(':', 1)
                    except ValueError:
                        # some time the field send by server is not good, there is a real space rather an encoded space
                        # exemple in my library : id:2806|artist:Bruno Mars | www.RNBxBeatz.com|
                        pass

                    if clef == 'id':
                        itemtampon.setProperty('artist_id', str(valeur))

                    elif clef == 'artist':
                        itemtampon.setLabel(valeur)
                        self.origine.listMenu_Feuilles_all_Artists.addItem(itemtampon)
                        xbmc.log('Id item dasn menu feuilles : ' + str(itemtampon.getProperty('artist_id')) + valeur, xbmc.LOGDEBUG)
                        itemtampon = xbmcgui.ListItem()

                percent = int(nbre_pour_calculer_buddydialog / int(nbre_a_recolter)) * 100
                buddydialog.update(percent)

            buddydialog.close()
            self.origine.all_Artists_populated = True

            # end if lister All Artist

        elif label_branche == 'Albums':
        #elif numeroItemSelectionBranche == 3:  # liste 'all Albums
            xbmc.log(' entrée dans le menu all albums du_plugin MyMusic', xbmc.LOGNOTICE)
            if self.origine.all_albums_populated:
                return

            # the same porcessing as all artists
            self.origine.InterfaceCLI.viderLeBuffer()
            self.origine.InterfaceCLI.sendtoCLISomething('info total albums ?')
            reponse = self.origine.InterfaceCLI.receptionReponseEtDecodage()
            try:
                nbre_a_traiter = reponse.split('|')
                nbre_total_albums = nbre_a_traiter.pop()
            except IndexError:
                debug('FNYI : recherche all Album nbre_a_traiter plugin.py', xbmc.LOGDEBUG)
                outils.functionNotYetImplemented()
                return

            buddydialog = xbmcgui.DialogProgress()
            buddydialog.create('look after ' + nbre_total_albums + ' Albums')

            start = 0
            step = 800
            end = step
            nbre_recolted = 0
            nbre_a_recolter = int(nbre_total_albums)
            nbre_restant = nbre_a_recolter
            nbre_restant_a_recolter = nbre_restant
            nbre_pour_calculer_buddydialog = 0
            percent = 0
            buddydialog.update(percent)
            compteur_buddy = 0
            while nbre_recolted < nbre_a_recolter:
                if nbre_restant_a_recolter > step:
                    requete = 'albums ' + str(start) + '  ' + str(end) + ' tags:ijls'
                    self.origine.InterfaceCLI.sendtoCLISomething(requete)
                    nbre_recolted = nbre_recolted + step
                    nbre_restant_a_recolter = nbre_restant_a_recolter - step # = nbre_a_recolter - nbre_recolted
                    start = start + step
                    end = start + step
                else:  #reste  moins d'items que le step
                    requete= 'albums ' + str(start) + ' ' + str(nbre_a_recolter)+ ' tags:ijls'
                    self.origine.InterfaceCLI.sendtoCLISomething(requete)
                    nbre_recolted = nbre_recolted + nbre_restant_a_recolter

                xbmc.log('la récolte a été bonne de  : ' + str(nbre_recolted), xbmc.LOGNOTICE)

                reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
                xbmc.log('Les albums unefoispropre : ' + str(reponsepropre), xbmc.LOGNOTICE)

                # if the buffer is truncated we need to colapse it
                while not ('count:' + str(nbre_total_albums)) in reponsepropre:
                    reponsepropre = reponsepropre + self.origine.InterfaceCLI.receptionReponseEtDecodage()

                # here we get a string with albums we need to analyse it
                # trim the tail count
                try:
                    lesItemsAlbums = reponsepropre.split('|count:')
                    xbmc.log('listetemp des Albums' + str(lesItemsAlbums), xbmc.LOGDEBUG)
                    lesItemsAlbums_text = lesItemsAlbums[0]
                except IndexError:
                    debug('FNYI : recherche all Album lesItemsAlbums plugin.py', xbmc.LOGDEBUG)
                    outils.functionNotYetImplemented()
                    return
                # trim the head :
                try:
                    index_du_debut = lesItemsAlbums_text.find('albums|' + str(start) + '|' + str(step) + '|')
                    xbmc.log('index count : ' + str(index_du_debut), xbmc.LOGDEBUG)
                    index_du_fin_de_titre = lesItemsAlbums_text.find('tags:ijls')
                    xbmc.log('index fin du  titre : ' + str(index_du_fin_de_titre), xbmc.LOGDEBUG)
                    lesItemsAlbumsNormalised = lesItemsAlbums_text[index_du_fin_de_titre : ]
                    xbmc.log('les Items Albums Normalised : ' + lesItemsAlbumsNormalised, xbmc.LOGNOTICE)
                except:
                    debug('FNYI : recherche all Album index_du_debut plugin.py', xbmc.LOGDEBUG)
                    outils.functionNotYetImplemented()

                    return

                # here we have a nice string of albums ' id:xxx|album:AAAA|id:yyy|album:BBBB etc...
                try:
                    lachainedesItemsAlbums = lesItemsAlbumsNormalised.split('|')  #
                    xbmc.log('chaine des items albums  : ' + str(lachainedesItemsAlbums), xbmc.LOGDEBUG)
                except:
                    debug('FNYI : recherche all Album lachainedesItemsAlbums plugin.py', xbmc.LOGDEBUG)
                    outils.functionNotYetImplemented()
                    return

                itemtampon = xbmcgui.ListItem()     # prepare le menulist
                # prepare update buddydialogprogress

                for chaine in lachainedesItemsAlbums:
                    nbre_pour_calculer_buddydialog = nbre_pour_calculer_buddydialog + 1
                    try:
                        clef, valeur = chaine.split(':', 1)
                    except ValueError:
                        # some time the field send by server is not good, there is a real space rather an encoded space
                        # exemple in my library : id:2806|artist:Bruno Mars | www.RNBxBeatz.com|
                        pass

                    if clef == 'id':
                        album_id = valeur
                        itemtampon.setProperty('album_id', album_id)

                    elif clef == 'album':
                        itemtampon.setLabel(valeur)

                    elif clef == 'artwork_track_id':
                        itemtampon.setProperty('artwork_track_id', str(valeur))

                    elif clef == 'textkey':
                        itemtampon.setProperty('textkey', valeur)

                        self.origine.listMenu_Feuilles_all_Albums.addItem(itemtampon)
                        debug('Id item album : ' + album_id  , xbmc.LOGNOTICE)
                        itemtampon = xbmcgui.ListItem()

                percent = int(nbre_pour_calculer_buddydialog / int(nbre_a_recolter)) * 100
                buddydialog.update(percent)

            buddydialog.close()

            # todo : extend the setArt each time the user go down in the list
            # for now just the 20 item of the list
            # because if the list (number of album) is very long take too much time
            # so dig the artwork by fragment
            for indice in range(20):
            #for indice in range(self.origine.listMenu_Feuilles_all_Albums.size() - 1 ):
                item = self.origine.listMenu_Feuilles_all_Albums.getListItem(indice)
                try:
                    artwork_track_id = item.getProperty('artwork_track_id')
                    debug('artwork_track_id : ' + str(artwork_track_id))
                    if artwork_track_id:
                        filename_coverart = self.get_artwork(hashcode_artwork=artwork_track_id)
                        item.setArt({'thumb': filename_coverart})
                        item.setProperty('image' , filename_coverart)
                except:
                    debug('could not get artwork')
                    #outils.functionNotYetImplemented()
            #fin loop for indice
            self.origine.all_albums_populated = True
        # end if lister All Albums

        #elif label_branche == 'Random mix'
        #elif numeroItemSelectionBranche == 8: #random mix
        # this will open a new frame  framePlaylist
        # first listen then launch the command and compute the answer
        #xbmc.log(' entrée dans le menu random mix du_plugin MyMusic', xbmc.LOGNOTICE)

        #all is erased and moved somewhere else  in the app ->
        #frameMenu:: update_random_mix_playlist

        elif label_branche == 'Music folder':
        #elif numeroItemSelectionBranche == 9:   # music folder call by frameMenu->

            debug(' entrée dans le menu music folder du_plugin MyMusic', xbmc.LOGNOTICE)
            if self.origine.all_dossiers_populated:
                return

            # the same porcessing as all artists
            self.origine.InterfaceCLI.viderLeBuffer()
            self.origine.InterfaceCLI.sendtoCLISomething('musicfolder')
            reponse = self.origine.InterfaceCLI.receptionReponseEtDecodage()
            try:
                nbre_a_traiter = reponse.split('|')
                count_dossiers = nbre_a_traiter.pop()
                countsplit = count_dossiers.split(':')
                nbre_total_dossiers = countsplit.pop()
            except IndexError:
                debug('erreur dans le nombre ' + str(nbre_a_traiter), xbmc.LOGNOTICE)
                outils.functionNotYetImplemented()
                return

            buddydialog = xbmcgui.DialogProgress()
            buddydialog.create('look after ' + nbre_total_dossiers + ' Folders ')

            start = 0
            step = 800
            end = step
            nbre_recolted = 0
            nbre_a_recolter = int(nbre_total_dossiers)
            nbre_restant = nbre_a_recolter
            nbre_restant_a_recolter = nbre_restant
            nbre_pour_calculer_buddydialog = 0
            percent = 0
            buddydialog.update(percent)
            while nbre_recolted < nbre_a_recolter:
                if nbre_restant_a_recolter > step:
                    self.origine.InterfaceCLI.sendtoCLISomething('musicfolder ' + str(start) + '  ' + str(end))
                    nbre_recolted = nbre_recolted + step
                    nbre_restant_a_recolter = nbre_restant_a_recolter - step # = nbre_a_recolter - nbre_recolted
                    start = start + step
                    end = start + step
                else:  #reste  moins d'items que le step
                    requete_construite = 'musicfolder ' + str(start) + ' ' + str(nbre_a_recolter)
                    self.origine.InterfaceCLI.sendtoCLISomething(requete_construite)
                    nbre_recolted = nbre_recolted + nbre_restant_a_recolter

                debug('la récolte a été bonne de  : ' + str(nbre_recolted), xbmc.LOGNOTICE)

                reponsepropre = self.origine.InterfaceCLI.receptionReponseEtDecodage()
                debug('Les albums unefoispropre : ' + str(reponsepropre), xbmc.LOGNOTICE)

                # if the buffer is truncated we need to colapse it
                while not ('count:' + str(nbre_total_dossiers)) in reponsepropre:
                    reponsepropre = reponsepropre + self.origine.InterfaceCLI.receptionReponseEtDecodage()

                # here we get a string with albums we need to analyse it
                # trim the tail count
                try:
                    lesItemsDossiers = reponsepropre.split('|count:')
                    xbmc.log('listetemp des Dossiers' + str(lesItemsDossiers), xbmc.LOGDEBUG)

                    lesItemsDossiers_text = lesItemsDossiers[0]
                except IndexError:
                    debug('erreur dans le nombre ' + str(lesItemsDossiers), xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()
                    return
                # trim the head :
                try:
                    index_du_debut = lesItemsDossiers_text.find('musicfolder ' + str(start) + ' ' + str(step) + '|')
                    debug('index count : ' + str(index_du_debut))
                    index_du_fin_de_titre = lesItemsDossiers_text.find('id')
                    debug('index fin du  titre : ' + str(index_du_fin_de_titre))
                    lesItemsDossiersNormalised = lesItemsDossiers_text[index_du_fin_de_titre : ]
                    debug('les Items Dossiers Normalised : ' + lesItemsDossiersNormalised, xbmc.LOGNOTICE)
                except:
                    outils.functionNotYetImplemented()

                    return

                # here we have a nice string of albums ' id:xxx|album:AAAA|id:yyy|album:BBBB etc...
                try:
                    lachainedesItemsDossiers = lesItemsDossiersNormalised.split('|')  #
                    debug('chaine des items albums  : ' + str(lachainedesItemsDossiers))
                except:
                    debug('functionNotYetImplemented recherche Dossiers plugin.py', xbmc.LOGNOTICE)
                    outils.functionNotYetImplemented()

                    return

                itemtampon = xbmcgui.ListItem()     # prepare le menulist
                # prepare update buddydialogprogress

                debug('à decrypter : ' + str(lachainedesItemsDossiers), xbmc.LOGNOTICE)

                for chaine in lachainedesItemsDossiers:
                    nbre_pour_calculer_buddydialog = nbre_pour_calculer_buddydialog + 1
                    debug('la chaine : ' + str(chaine), xbmc.LOGNOTICE)
                    try:
                        clef, valeur = chaine.split(':', 1)
                    except ValueError:
                        # some time the field send by server is not good, there is a real space rather an encoded space
                        # exemple in my library : id:2806|artist:Bruno Mars | www.RNBxBeatz.com|
                        pass

                    if clef == 'id':
                        itemtampon.setProperty('folder_id', str(valeur))

                    elif clef == 'filename':
                        itemtampon.setProperty(clef, valeur)
                        itemtampon.setLabel(valeur)

                    elif clef == 'type':
                        itemtampon.setProperty(clef , valeur)
                        if valeur == 'folder':
                            itemtampon.setArt({'thumb': self.image_folder})
                        self.origine.listMenu_Feuilles_all_Dossiers.addItem(itemtampon)
                        debug('Id item dossier : ' + str(itemtampon.getProperty('folder_id')) + valeur, xbmc.LOGNOTICE)
                        itemtampon = xbmcgui.ListItem()

                percent = 100 * int(nbre_pour_calculer_buddydialog / int(nbre_a_recolter))
                buddydialog.update(percent)

            buddydialog.close()
            self.origine.all_dossiers_populated= True
        # end if lister musicfolder

        else:
            outils.functionNotYetImplemented()

        # fin fonction le_menu_feuille, class Plugin_MyMusic

    def le_menu_fleurs(self, plugOrigine ,  numeroItemSelectionFeuille):
        '''

        :param numeroItemSelectionFeuille:
        :return:
        '''
        if plugOrigine == 'All Artists':

            xbmc.log(' entrée dans le_menu_fleur_All_Artists_du_plugins MyMusic', xbmc.LOGNOTICE)

            '''
            exemple :
            artists 0 10 artist_id:4370
            artists 0 10 artist_id%3A4370 id%3A4370 artist%3AA.%20Gainsbourg%2FSerge%20Gainsbourg count%3A1
            albums 0 10 artist_id:4370
            albums 0 10 artist_id%3A4370 id%3A1935 album%3ANo.%202 count%3A1
            albums 0 10 artist_id:4370 tags:aCdejJKlstuwxy
            albums 0 10 artist_id%3A4370 tags%3AaCdejJKlstuwxy id%3A1935 album%3ANo.%202 year%3A2003 
            artwork_track_id%3Ab38f7f8a title%3ANo.%202 compilation%3A0 artist%3ASerge%20Gainsbourg textkey%3AN count%3A1
            the cover is there : http://192.168.1.101:9000/music/b38f7f8a/cover.jpg
            '''
            artist = self.origine.listMenu_Feuilles_all_Artists.getListItem(
                        self.origine.listMenu_Feuilles_all_Artists.getSelectedPosition()).getLabel()
            #title = self.origine.listMenu_Feuilles_all_Artists.getListItem(numeroItemSelectionFeuille).getLabel()
            # same :
            #itemdelisteOrigine = self.origine.listMenu_Feuilles_all_Artists.getListItem(numeroItemSelectionFeuille)
            #labeldetete = itemdelisteOrigine.getLabel()

            # affichage nouvelle fenêtre:
            self.frameAllArtists = frameMyMusicAllArtists.MyMusicAllArtists()

            self.frameAllArtists.listMenu_principal.reset()

            #self.frameAllArtits.show()

            self.origine.InterfaceCLI.viderLeBuffer() # need because resiliersouscription() let some data in the buffer
            requete = 'albums 0 100 artist_id:' + numeroItemSelectionFeuille + ' tags:' + TAGS
            self.origine.InterfaceCLI.sendtoCLISomething(requete)

            reception = self.origine.InterfaceCLI.receptionReponseEtDecodage()

            try:
                nbre_a_traiter = reception.split('count:')
                nombreDItems = nbre_a_traiter.pop()
            except IndexError:
                outils.functionNotYetImplemented()

            try:
                nbreEntier = int(nombreDItems)
            except:
                outils.functionNotYetImplemented()

            #trim head and queue
            try:
                poubelle, tampon = reception.split(TAGS+'|')
                lesItemsAlbumsNormalised , poubelle = tampon.split('|count:')
            except ValueError:
                outils.functionNotYetImplemented()

            try:
                lachainedesItemsAlbums = lesItemsAlbumsNormalised.split('|')  #
                debug('Plugin_music:: Fleurs chainedesAlbums : ' + str(lachainedesItemsAlbums), xbmc.LOGNOTICE)
            except:
                debug('functionNotYetImplemented plugin_music::fleurs', xbmc.LOGNOTICE)
                outils.functionNotYetImplemented()

            nombrearanger = 0
            index = 0

            itemtampon = xbmcgui.ListItem()
            for chaine in lachainedesItemsAlbums:
                debug('chainedesItemsAlbumsdelartiste : ' + chaine, xbmc.LOGNOTICE)
                try:
                    clef, valeur = chaine.split(':', 1)
                except ValueError:
                    pass

                if clef == 'id':
                    itemtampon.setProperty(clef, valeur)
                    itemtampon.setProperty('cmd', 'albums')
                    itemtampon.setProperty('artist_id' , numeroItemSelectionFeuille)
                    itemtampon.setProperty('artist', artist)

                elif clef == 'album':
                    itemtampon.setLabel(valeur)
                elif clef == 'artwork_track_id':
                    hascode_coverart = valeur
                    filename_coverart = self.get_artwork(hashcode_artwork=hascode_coverart)
                    itemtampon.setArt({'thumb': filename_coverart})
                    itemtampon.setProperty('image', filename_coverart)

                elif clef == 'textkey':
                    self.frameAllArtists.listMenu_principal.addItem(itemtampon)
                    itemtampon = xbmcgui.ListItem()
                else:
                    itemtampon.setProperty(clef,valeur)

            self.frameAllArtists.listMenu_principal.setVisible(True)
            self.frameAllArtists.doModal()
            del self.frameAllArtists
        #fin if All_Artist


        elif plugOrigine == 'ArtistAlbums':

            debug(' entrée dans plugin.py.MyMusic.le_menu_fleur', xbmc.LOGNOTICE)
            album = self.origine.listMenu_Feuilles_ArtistAlbums.getListItem(
                self.origine.listMenu_Feuilles_ArtistAlbums.getSelectedPosition()).getLabel()
            # title = self.origine.listMenu_Feuilles_all_Artists.getListItem(numeroItemSelectionFeuille).getLabel()
            # same :
            # itemdelisteOrigine = self.origine.listMenu_Feuilles_all_Artists.getListItem(numeroItemSelectionFeuille)
            # labeldetete = itemdelisteOrigine.getLabel()

            # affichage nouvelle fenêtre:
            self.frameArtistAlbums = frameMyMusicAlbums.MyMusicAllAlbums()

            # self.frameAlbums.show()

            self.origine.InterfaceCLI.viderLeBuffer()  # need because resiliersouscription() let some data in the buffer
            requete = 'albums 0 100 album_id:' + numeroItemSelectionFeuille + ' tags:' + TAGS
            self.origine.InterfaceCLI.sendtoCLISomething(requete)

            reception = self.origine.InterfaceCLI.receptionReponseEtDecodage()

            try:
                nbre_a_traiter = reception.split('count:')
            except ValueError:
                pass

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
                poubelle, tampon = reception.split(TAGS + '|')
                lesItemsAlbumsNormalised, poubelle = tampon.split('|count:')
            except ValueError:
                return

            try:
                lachainedesItemsAlbums = lesItemsAlbumsNormalised.split('|')  #
                xbmc.log('Plugin_music:: Fleurs chainedesAlbums : ' + str(lachainedesItemsAlbums), xbmc.LOGNOTICE)
            except:
                xbmc.log('functionNotYetImplemented plugin_music::fleurs::Albums', xbmc.LOGNOTICE)
                outils.functionNotYetImplemented()

                return

            itemtampon = xbmcgui.ListItem()
            for chaine in lachainedesItemsAlbums:

                try:
                    clef, valeur = chaine.split(':', 1)
                except ValueError:
                    pass

                if clef == 'id':
                    itemtampon.setProperty(clef, valeur)
                    itemtampon.setProperty('cmd', 'ArtistAlbums')
                    itemtampon.setProperty('album_id', numeroItemSelectionFeuille)

                elif clef == 'album':
                    itemtampon.setLabel(valeur)

                elif clef == 'artwork_track_id':
                    hascode_coverart = valeur
                    filename_coverart = self.get_artwork(hashcode_artwork=hascode_coverart)
                    itemtampon.setArt({'thumb': filename_coverart})
                    itemtampon.setProperty('image', filename_coverart)


                # elif clef == 'year':
                #    title
                #    compilation
                #    artist

                elif clef == 'textkey':
                    itemtampon.setProperty(clef, valeur)
                    self.frameArtistAlbums.listMenu_principal.addItem(itemtampon)
                    itemtampon = xbmcgui.ListItem()
                else:
                    itemtampon.setProperty(clef, valeur)

            self.frameArtistAlbums.listMenu_principal.setVisible(True)
            self.frameArtistAlbums.doModal()
            del self.frameArtistAlbums
        # fin if ArtistAlbums

        elif plugOrigine == 'Albums':

            xbmc.log(' entrée dans le_menu_fleur_Albums_du_plugins MyMusic', xbmc.LOGNOTICE)
            album = self.origine.listMenu_Feuilles_all_Albums.getListItem(
                self.origine.listMenu_Feuilles_all_Albums.getSelectedPosition()).getLabel()
            # title = self.origine.listMenu_Feuilles_all_Artists.getListItem(numeroItemSelectionFeuille).getLabel()
            # same :
            # itemdelisteOrigine = self.origine.listMenu_Feuilles_all_Artists.getListItem(numeroItemSelectionFeuille)
            # labeldetete = itemdelisteOrigine.getLabel()

            # affichage nouvelle fenêtre:
            self.frameAllAbums = frameMyMusicAlbums.MyMusicAllAlbums()

            #self.frameAllAlbums.show()

            self.origine.InterfaceCLI.viderLeBuffer()  # need because resiliersouscription() let some data in the buffer
            self.origine.InterfaceCLI.sendtoCLISomething(
                'albums 0 100 album_id:' + numeroItemSelectionFeuille + ' tags:' + TAGS)

            reception = self.origine.InterfaceCLI.receptionReponseEtDecodage()

            try:
                nbre_a_traiter = reception.split('count:')
            except ValueError:
                pass

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
                poubelle, tampon = reception.split(TAGS + '|')
                lesItemsAlbumsNormalised, poubelle = tampon.split('|count:')
            except ValueError:
                return

            try:
                lachainedesItemsAlbums = lesItemsAlbumsNormalised.split('|')  #
                xbmc.log('Plugin_music:: Fleurs chainedesAlbums : ' + str(lachainedesItemsAlbums), xbmc.LOGNOTICE)
            except:
                xbmc.log('functionNotYetImplemented plugin_music::fleurs::Albums', xbmc.LOGNOTICE)
                outils.functionNotYetImplemented()

                return

            itemtampon = xbmcgui.ListItem()
            for chaine in lachainedesItemsAlbums:

                try:
                    clef, valeur = chaine.split(':', 1)
                except ValueError:
                    pass

                if clef == 'id':
                    itemtampon.setProperty(clef, valeur)
                    itemtampon.setProperty('cmd', 'albums')
                    itemtampon.setProperty('album_id' , numeroItemSelectionFeuille)

                if clef == 'id':
                    itemtampon.setProperty(clef, valeur)
                    itemtampon.setProperty('album_id', numeroItemSelectionFeuille)

                elif clef == 'album':
                    itemtampon.setLabel(valeur)

                elif clef == 'artwork_track_id':
                    hascode_coverart = valeur
                    filename_coverart = self.get_artwork(hashcode_artwork=hascode_coverart)
                    itemtampon.setArt({'thumb': filename_coverart})
                    itemtampon.setProperty('image', filename_coverart)



                # elif clef == 'year':
                #    title
                #    compilation
                #    artist

                elif clef == 'textkey':
                    itemtampon.setProperty(clef , valeur)
                    self.frameAllAbums.listMenu_principal.addItem(itemtampon)
                    itemtampon = xbmcgui.ListItem()
                else:
                    itemtampon.setProperty(clef, valeur)

            self.frameAllAbums.doModal()
            del self.frameAllAbums
        #fin if all Albums

        elif plugOrigine == 'Dossiers':

            xbmc.log(' entrée dans le_menu_fleur_Dossiers_du_plugins MyMusic', xbmc.LOGNOTICE)
            album = self.origine.listMenu_Feuilles_all_Dossiers.getListItem(
                self.origine.listMenu_Feuilles_all_Dossiers.getSelectedPosition()).getLabel()

            # affichage nouvelle fenêtre:
            self.frameFolders = frameMusicFolder.ViewMusicFolder()
            #self.frameFolders.show()

            # initialise focus ans navigation
            self.origine.InterfaceCLI.viderLeBuffer()  # need because resiliersouscription() let some data in the buffer
            self.origine.InterfaceCLI.sendtoCLISomething(
                'musicfolder 0 100 folder_id:' + numeroItemSelectionFeuille)

            reception = self.origine.InterfaceCLI.receptionReponseEtDecodage()

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
                xbmc.log('Plugin_music:: Fleurs chainedesDossiers : ' + str(lachainedesItemsDossiers), xbmc.LOGNOTICE)
            except:
                xbmc.log('functionNotYetImplemented plugin_music::fleurs::Dossiers', xbmc.LOGNOTICE)
                outils.functionNotYetImplemented()

                return

            itemtampon = xbmcgui.ListItem()
            for chaine in lachainedesItemsDossiers:

                try:
                    clef , valeur = chaine.split(':', 1)
                except ValueError:
                    pass

                if clef == 'id':
                    itemtampon.setProperty(clef, valeur)
                    itemtampon.setProperty('folder_parent_id' , numeroItemSelectionFeuille)

                elif clef == 'filename':
                    itemtampon.setLabel(valeur)

                elif clef == 'type':
                    itemtampon.setProperty(clef, valeur)
                    if valeur == 'folder':
                        itemtampon.setArt({'thumb': self.image_folder})
                    elif valeur == 'track':
                        debug('set art for track',xbmc.LOGNOTICE)
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

                    self.frameFolders.listMusicFolder.addItem(itemtampon)
                    itemtampon = xbmcgui.ListItem()

            self.frameFolders.doModal()
            #xbmc.Monitor().waitForAbort()
            del self.frameFolders
        #fin if Plugorigine Dossier
    # fin fonction le_menu_fleurs
# fin class MyMusic


class Extras(Plugin_Generique):
    '''not yet  used Todo
    only a structural thing to think about
    perhaps never used
    '''

    def le_menu_branche(self, numeroItemSelection):
        # not here
        pass

    def le_menu_feuille(self, numeroItemSelection):
        if numeroItemSelection == 0:
            # players action
            outils.functionNotYetImplemented()

            return
        elif numeroItemSelection == 1:
            # music source
            outils.functionNotYetImplemented()

            return
        elif numeroItemSelection == 2:
            #don't stop the music
            outils.functionNotYetImplemented()

            return