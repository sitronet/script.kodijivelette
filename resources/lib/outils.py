#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Doc générale : Une complète liste des commandes sur l'interface CLI
   est disponible dans le fichier :
   logitechmediaserver-7.9.2-1529332109-arm-linux/Slim/Control/Request.pm
   logitechmediaserver-7.7.6/Slim/Plugin/CLI/Plugin.pm

   Also :
   http://<LMSServer>:9000/html/docs/help.html

    pour cette classe de découverte voir :
    Référence :logitechmediaserver-7.7.6/Slim/Networking/Discovery/Server.pm


   '''
Kodi = True
if Kodi:
    import xbmc
    import xbmcgui


    ADDON_ID = 'script.kodijivelette'
    KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])
    KODILANGUAGE = xbmc.getLanguage(xbmc.ISO_639_1)

import logging
import socket
import time
import urllib
import random

#from ConnexionClient import InterfaceCLIduLMS

def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper


@singleton
class WhereIsTheLMSServer:

    def __init__(self):
        self.url = '255.255.255.255'
        self.port = 3483
        #self.logger = logging.getLogger()
        self.LMSnom = 'toto'
        self.LMSip = ''
        self.LMSUUID = ''
        self.LMSversion = ''
        self.LMSCLIip = ''
        self.LMSUDPport = 3483
        self.LMSversion = ''
        self.LMSwebport = ''
        self.LMSCLIport = 9090  # à initialiser en paramètre (setting)par defaut =9090  sauf changement effectué
        # par le propriétaire du serveur LMS
        self.Etape = ''

    def decodageduDataGram(self, reponse):
        """
        Decodage du DataGram
        # reponse est le bloc recu dans le datagramme de reponse du serveur LMS
        ou bien du datagramme recu en ecoute
        # on cherche a decoder  l'information contenue à l'interieur
        # du peu que j'en sais sur sa structure :
        # exemple reel :
        # b'ENAME\x06NAS542JSON\x049000UUID$c26ea8e4-d809-4824-a3c6-6f49109cf57cVERS\x057.9.2'
        il est etrange que dans cet exemple réel l'UUID ne contient pas de separateur, est-ce une erreur
        de prog sur le serveur Perl ?

        Apres avoir lu le code java de nickClayton, je comprends que le séparateur n'est que
        '0' ,  suivi de la longueur de la réponse , ca fait du datagram super comprimé
        ca veut probablement dire aussi que la longueur a une limite maximale
        Dans l'exemple : b'NAME\x06NAS542'   NAS542 fait 6 octets d'ou le separateur x0 plus l'octet de valeur 6
                         b'JSON\x049000'     9000 fait 4 octets d'ou le separateur plus l'octet de valeur 4

        # une fois compris la logique et la structure de l'information c'est facile à decoder


        # Ici, j'utilise la facilite des tuples en decoupant la
        # reponse selon les chaînes connues et en enlevant progressivement
        # les informations
        # pour cela je demarre à la fin de la chaine pour la remonter au début
        # VERS , UUID , JSON , NAME
        # remarque : il manque IPAD dans la reponse de mon serveur
        # est-ce local à mon serveur ou commun tous les serveurs ?
        Si c'est local il faudra trouver une autre méthode

        Exercice : réecrire cette fonction en utilisant uniquement les types listes , mais est ce possible ?
        Exercice : réecrire cette fonction en utilisant uniquement les primitives sur les types str
        Exercice : réecrire cette fonction en utilisant itération d'une seule fonction générique pour décoder les champs
        début :
         chaineDeRecherche = [ VERS, UUID, JSON, NAME ] , liste, dict ou vecteur ?
         for chaine in chaineDeRecherche:
            ...

        return les valeurs recherchées sont stockées dans les variables

        """
        if Kodi:
            xbmc.log("decodage de la trame : " , xbmc.LOGNOTICE)
            xbmc.log(reponse, xbmc.LOGNOTICE)
        else:
            print ('decodage de la trame : ' + reponse)
        #octetlongueurInfo = 0

        # recherche de la version
        Recherche = b''  # est-ce que ceci fonctionne en python 2 , Change-t-il de classe lors de l'assignation ?
        Recherche = reponse.split(b'VERS')
        (PremierduTuple, SecondduTuple) = Recherche  # type  python 2 mais 3 ?
        #octetlongueurInfo = 1
        octetlongueurInfo = int(ord(SecondduTuple[0])) # python 2 ne reconnait pas les caractère genre \x05
        # pour 5 octets de long alors que ca marche bien en python 3 , alors en pyhton 2 il faut ruser avec ordinal,
        # entier etc...
        # Rappel un entier python est sur 4 octets, il n'existe pas le short int
        # quel est donc le typage d'un truc d'un octet en python ? -> bytes() ? humhum ca existe en python2 ?
        #octetlongueurInfo = int(SecondduTuple[0]) # -> fonctionne en python 3.7 uniquement mais kodi est en 2.xx
        # Exercice : écrire avec décalage bit à bit . # est-ce que les fonctions sur les bits existent en python ?
        octetlongueurInfo += 1
        Recherche = SecondduTuple[1:octetlongueurInfo]
        self.LMSversion = Recherche.decode('ascii')
        if Kodi:
            xbmc.log('La version du Serveur  est : ' + self.LMSversion , xbmc.LOGNOTICE)
        else:
            print ('La version du Serveur est : \t' + self.LMSversion)

        # recherche de l'UUID
        Recherche = PremierduTuple.split(b'UUID')
        (PremierduTuple, SecondduTuple) = Recherche
        self.LMSUUID = SecondduTuple.decode('ascii')
        if Kodi:
            xbmc.log('l UUID du serveur est : ' + self.LMSUUID , xbmc.LOGNOTICE)
        else:
            print ('l UUID du serveur est : \t  \t' + self.LMSUUID)

        # recherche du webport
        Recherche = PremierduTuple.split(b'JSON')
        (PremierduTuple, SecondduTuple) = Recherche
        octetlongueurInfo = int(ord(SecondduTuple[0]))
        Recherche = SecondduTuple[1:octetlongueurInfo + 1]
        self.LMSwebport = Recherche.decode('ascii')
        if Kodi:
            xbmc.log('le port sur serveur Web est : ' + self.LMSwebport , xbmc.LOGNOTICE)
        else:
            print ('le port sur serveur Web est : \t' + self.LMSwebport)

        # recherche du nom
        Recherche = PremierduTuple.split(b'NAME')
        (PremierduTuple, SecondduTuple) = Recherche
        Recherche = SecondduTuple
        octetlongueurInfo = int(ord(SecondduTuple[0]))
        Recherche = SecondduTuple[1:octetlongueurInfo + 1]
        self.LMSnom = Recherche.decode('ascii')
        if Kodi:
            xbmc.log('le nom du serveur est : ' + self.LMSnom , xbmc.LOGNOTICE)
        else:
            print ('le nom du serveur est : \t   \t%s' % self.LMSnom)
        return

    def decodageduDataGram_alternate(self, reponse):
        '''
        The chalenge is :
        rewriting the previous function decode_datagram() with an other conceptual meaning
        todo

        :param reponse:
        :return:
        '''
        if Kodi:
            xbmc.log("decodage de la trame : " , xbmc.LOGNOTICE)
            xbmc.log(reponse, xbmc.LOGNOTICE)
        else:
            print ('decodage de la trame : ' + reponse)

        # Todo : use of JSON, is it possible ?
        #
        #Recherche = reponse.split(b'\0')
        # #
        # Todo : blabla
        #
            if Kodi:
                xbmc.log('le nom du serveur est :' + self.LMSnom, xbmc.LOGNOTICE)
            else:
                print ('le nom du serveur est : ' +  self.LMSnom)
        return

    def Ecoute(self): # fonction pas encore utilisée, ça viendra plus tard
        '''
        Cette fonction est pour un usage futur

        le serveur LMS envoie des paquet UDP en broadcast toutes les 60 secondes
        cela peut nous permettre de découvrir de nouveaux serveur sur le réseau
        :return:
        '''
        bufferduSocket = 1024
        adresse = ('', self.port)
        socketEcoute = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketEcoute.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        socketEcoute.bind(adresse)
        logging.info("serveur en écoute ...")
        Noreponse = True
        while Noreponse:
            # attente d'une nouvelle connexion
            # et enregistrement de la requete et de l'adresse du demandeur
            requete, adresseclient = socketEcoute.recvfrom(bufferduSocket)
            logging.info(requete)
            requete = requete.strip()
            logging.info(requete)
            logging.info(adresseclient)
            Noreponse = False
            '''
            TODO : réflechir à l'utilité de cette fonction, ou bien 
            relancer request_discovery() 
            '''
        socketEcoute.close()

    def RequeteExploratoire(self):
        '''
        Exploration du réseau pour savoir si un serveur LMS est présent.
         Discovery of the LMS on the network.
         Dans le détail de cette fonction :
         Requete qui envoie un datagramme UDP sur le réseau
         Ce datagram contient une requete (e vs E ) pour savoir si un serveur existe sur le réseau
         si un LMS existe, il écoute la requête et y répond en donnant les infos demandées dans le champs de la
         requête i.e : E
         --------------------------
         From nickClayton :

         'e', // 'existe-t-il ?'
                'I', 'P', 'A', 'D', 0, // Include IP address
                'N', 'A', 'M', 'E', 0, // Include server name
                'UUID                  // monAjout
                'J', 'S', 'O', 'N', 0, // Include server port du service web (HTTP)
                'JVID' What's that ?   from code squeezeplay
         ----------------------------
         il n'y a pas moyen de connaître le port de l'interface CLI par ce procédé
         J'assigne celui par défaut : 9090

        take care that the begin start by e or E
        e is a query
        E is an answer

        more :
        The LMS send with regularity a request datagram over UDP with a 26 byte lentgh
        of course the request start with e (query)
        once this main controler is launched we can continue to scan
        the port 3483 (udp) to see if other LMS could appear
        or the LMS change its ip adress.
        probably it is possible to do that in a separate thread ans send event to signal the change to the main.
        this will be in the other function Ecoute() to be implemented (todo)

        Fonction à modifier et tenter de mettre un unique séparateur de champs différent pour voir si le serveur utilise
        le même séparateur de champs que la requête
        '''

        self.Etape = 'Exploring Network...'
        buffer = 1024
        adresse = ('<broadcast>', self.port)
        # l'ordre du datagram est important pour la fonction de décodage
        # le serveur répond dans l'ordre de la question
        # changer l'ordre implique de changer la fonction décodage
        try:
            data = bytes('eIPAD\x00NAME\x00JSON\x00UUID\x00VERS\x00', 'ascii') #python 3.7
        except TypeError:
            data = bytes('eIPAD\x00NAME\x00JSON\x00UUID\x00VERS\x00\JVID\x00')  # python 2.7
        #print type(data)


        # création du socket UDP
        if Kodi:
            #xbmc.log("creation du socket, envoi du datagram de découverte" + str(data) , xbmc.LOGDEBUG) # erreur sur kodi
            xbmc.log("creation du socket, envoi du datagram de découverte" , xbmc.LOGDEBUG)
        else:
            print ("creation du socket, envoi du datagram de découverte")

        monSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        monSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Set a timeout so the socket does not block
        # indefinitely when trying to receive data.
        monSocket.settimeout(0.2)
        # envoi de la requête au serveur
        try:
            monSocket.sendto(data, adresse)
        except:
            if Kodi:
                xbmc.log("pas de connexion réseau" , xbmc.LOGNOTICE)
            else:
                print ("pas de connexion réseau")
            exit(1)
        reponse = ''
        adr = ('', '')
        # réception et affichage de la réponse
        timeout = time.time() + 2.0
        while not reponse:
            if (time.time() >  timeout):
                break
            try:
                reponse, adr = monSocket.recvfrom(buffer)
                Eureka = True
            except:
                Eureka = False
                if Kodi:
                    xbmc.log("connecté au réseau mais pas de réponse d'un serveur" , xbmc.LOGNOTICE)
                else:
                    print ("connecté au réseau mais pas de réponse d'un serveur")
        if Kodi:
            xbmc.log("réponse => %s" % reponse, xbmc.LOGNOTICE) # marche sur kodi ?
        else:
            print ( '======réponse======>' + str(reponse.split(bytes(' '))))
            # exemple de reponse :
            # 'ENAME\x06NAS542JSON\x049000UUID$c26ea8e4-d809-4824-a3c6-6f49109cf57cVERS\x057.9.2'

        (self.LMSCLIip, self.LMSUDPport) = adr
        if Kodi:
            xbmc.log('adresse du serveur LMS : ' + self.LMSCLIip , xbmc.LOGNOTICE)
            xbmc.log('port de l interface d ecoute des players de LMS :' + str(self.LMSUDPport) , xbmc.LOGNOTICE)
        else:
            print ('adresse du serveur LMS : ' + self.LMSCLIip )
            print ('port de l interface d ecoute des players de LMS :' + str(self.LMSUDPport))

        # nous avons un joli paquet , maintenant il faut savoir ce qu'il a dedans, on appelle une fonction de notre crû
        # qui va s'en occuper
        self.decodageduDataGram(reponse)
        # fermeture de la connexion
        monSocket.close()
        if Kodi:
            xbmc.log("fin du client UDP de recherche du Serveur" , xbmc.LOGNOTICE)
        else:
            print ("++++++++fin du client UDP de recherche du Serveur+++++++")
        return Eureka

    def DonnonsAMangerAKodi(self): # pas utilisé , est-ce que ca peut servir ?
        '''
        passe les paramètres trouvés à la configuration du plugin pour kodi
        Not Yet Used
        :return:
        '''
        # publish lmsdetails as window properties for the plugin entry
        if Kodi:
            self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            self.win.setProperty("LMSname", self.LMSnom)
            self.win.setProperty("LMSCLIip", self.LMSCLIip)
            self.win.setProperty("LMSWebport", self.LMSwebport)
            for x in self.listePlayers:
                self.win.setProperty("LMSPlayer" + x, self.player[x])
        else:
            # plateforme de test standard pas de kodi plateforme
            # define tkinter
            pass

@singleton
class WhatAreThePlayers():  # pas utilisé , ou cela va servir ?

    def __init__(self):
        self.listePlayers = []
        self.playerSelection = ''
        self.dictionnairedesPlatines = {}

    def combienDePlayers(self):
        pass


    def get_volume_player(self):
        pass

    def recherchedesPlayers(self, InterfaceCLI, recevoirEnAttente):
        '''
        fonction de recherche des players,
        Look after the receivers, for this task ask the server, use for that the interfaceCLIduLMS instance running in a
        separate Thread
        :param InterfaceCLI:
        :return:
        '''
        self.recevoirEnAttente = recevoirEnAttente

        #self.envoiEnAttente.set()  # ok it's the first something is sent don't need to wait anything
        InterfaceCLI.sendtoCLISomething('player count ?')   # nbre de receiver ?
        recu_ext = InterfaceCLI.receptionReponseEtDecodage()
        #self.recevoirEnAttente.wait(10)                      # waiting that we have the flag receive ok
        #recu_ext = InterfaceCLI.dataExchange # here the flag is ok, sommething has been received or the time is elapsed
                                             # so the content of the data comming from the LMS is now in the
                                             # recu_ext variable that we need to analyse
        #InterfaceCLI.dataExchange = ''       # clear the exchange buffer
        #self.recevoirEnAttente.clear()       # reset the Event object as we got the data stored in recu_ext
        b = recu_ext.split('|')                 # eclate la trame dans une liste selon les espaces
        count_str = b.pop()                  # on sait que ce champs est le nombre de player
        count_int = int(count_str)           # and did the stuff
        xbmc.log(recu_ext, xbmc.LOGNOTICE)   # log when testing the programm -> to suppress later (pb : codage)
        #informationText = ['nbre players : ' + count_str ]    #  text that will be show on the screen in the informational box
        #self.update_textbox(informationText)
          # so we know and print  the number of players what next ?
        xbmc.log("il y a " + count_str + "receivers , cool ", xbmc.LOGNOTICE)
        if count_int == 0:
            line1 = " No receiver to listen to music."
            line2 = " ...Exit...Error n° 35 "
            xbmcgui.Dialog().ok( ADDON_ID, line1 , line2 )
            # no player
            #informationText.append('no player to listen...Exit program')
            xbmc.log(" pas de platine pour jouer de la musique", xbmc.LOGNOTICE)
            xbmc.Monitor().waitForAbort(5)
            exit(35)

        InterfaceCLI.sendtoCLISomething('players 0 ' + count_str  ) # recherchons les players dont nous savons le nbre
        self.recevoirEnAttente.wait(10)
        recu_ext = InterfaceCLI.dataExchange                        # la réponse est dans recu_ext
        InterfaceCLI.dataExchange =''
        self.recevoirEnAttente.clear()

        b = recu_ext.split()                                        # on éclate la réponse dans une liste temporaire b
                                                                    # en coupant aux espaces
        c= "|".join(b)                                              # on rebobine tout dans un string avec un autre séparateur
        '''
        exemple trame c = 
                players|0|3|count%3A3|
                playerindex%3A0|playerid%3Ab8%3A27%3Aeb%3Acf%3Af2%3Ac0|uuid%3A|ip%3A192.168.1.15%3A50102|name%3ApiCorePlayer|
                seq_no%3A0|model%3Asqueezelite|modelname%3ASqueezeLite|power%3A0|isplaying%3A0|displaytype%3Anone|isplayer%3A1|
                canpoweroff%3A1|connected%3A1|firmware%3Av1.9.2-1158-pCP|
                playerindex%3A1|playerid%3A192.168.1.33|uuid%3A|ip%3A192.168.1.33%3A51064|name%3AMozilla%20de%20192.168.1.33|
                seq_no%3A0|model%3Ahttp|modelname%3AWeb%20Client|power%3A1|isplaying%3A1|isplayer%3A0|canpoweroff%3A0|
                connected%3A0|firmware%3A|
                playerindex%3A2|playerid%3A00%3A04%3A20%3A17%3A1c%3A44|uuid%3A21ec511edaa5a094fdb5301d7fa44c07|
                ip%3A192.168.1.17%3A41620|name%3ASqueezebox%20Receiver|seq_no%3A0|model%3Areceiver|
                modelname%3ASqueezebox%20Receiver|power%3A0|isplaying%3A0|displaytype%3Anone|isplayer%3A1|canpoweroff%3A1|
                connected%3A1|firmware%3A77'''

        d = urllib.unquote(c)                               # decodage escape web du string
        xbmc.log('String d ' + d, xbmc.LOGNOTICE)
        listedesplayers  = d.split('playerindex')                   # une liste de  X receivers + début de trame (X+1)
        if count_int == len(listedesplayers) - 1:
            pass
        else:
            xbmc.log("There is a little bug : the number of players is not what it should", xbmc.LOGNOTICE)
            line1 =  'There is a little bug : the number of players is not what it should'
            xbmcgui.Dialog().ok(ADDON_ID, line1)

        # pompé de https://stackoverflow.com/questions/21549809/how-to-create-dynamic-dictionary-names
        # accès aux players par dictionnairedesPlayers[1/2/3/...] - 0 est réservé au nombre de player
        dictionnairedesPlayers = [{} for _ in range(len(listedesplayers))]
        xbmc.log('dictionnaire des players : ' + str(dictionnairedesPlayers), xbmc.LOGNOTICE)
            # c'est magique !
        # noter que :
        # dictionnairedesPlayers est une liste
        # dictionnairedesPlayers[x] sont des dictionnaires
        # on peut changer en d = [[] for _ in range(len(listedesplayers))] : liste de liste
        # ou bien            d = [() for _ in range(len(listedesplayers))] : liste de tuple
        # mais on ne peut pas    {{} for _ in range(len(listedesplayers))} : pas possible

        nombredeplayers = 0
        line1 = ''
        for x in range(1, len(listedesplayers)):  # on ne s'occupe pas du début de la trame dans l'index [0]
            # dictionnaire pour un player [x]
            nombredeplayers = nombredeplayers + 1
            print (type(dictionnairedesPlayers[x]))
            swapa = listedesplayers[x]
            swapb = swapa.split('|')  # une nouvelle liste swapb temporaire
            xbmc.log('liste spliter swapb ' + str(swapb), xbmc.LOGDEBUG)
            print("print p.A : " + str(swapb))
            # pb pour chaque player dans la liste des players
            playerindex = swapb[0].lstrip(':')
            swapb.pop(0)
            for y in range(0, len(swapb) - 1):
                # on range cette liste dans une belle liste à deux dimensions
                if (swapb[y].find('playerid') >= 0):
                    (ajeter, playerid) = swapb[y].split('playerid:')  # pb résolu pour adresse mac avec : dans playerid
                    print('boucle_y p.A :  ' + playerid)
                    # swapb.pop(y)
                else:
                    clef, valeur = swapb[y].split(':', 1)
                    dictionnairedesPlayers[x][clef] = valeur
                    # xbmc.log(str(clef) + ' ++  ' + str(dictionnaireunplayer[clef]), xbmc.LOGNOTICE)
                    # print(" Boucle_y p.B : " + str(dictionnaireunplayer.items()))

            dictionnairedesPlayers[x]['playerid'] = playerid
            dictionnairedesPlayers[x]['playerindex'] = playerindex
            xbmc.log('le simple dico d un player : ' + str(dictionnairedesPlayers[x]), xbmc.LOGNOTICE)

        # line1 = 'Found at least one player : ' + '\n' + \
        #        'nom du player : ' + dictionnairedesPlayers[x]['name'] + '\n' + \
        #        ' playerid : ' + dictionnairedesPlayers[x]['playerid'] + '\n' + \
        #        ' model : ' + dictionnairedesPlayers[x]['modelname'] + '\n'
        # line2 = "Cool"

        # todo : à modifier le dialog , est-il nécessaire ? \
        # de plus pertube l'affichage lors du changement d'état dans les menus
        # xbmcgui.Dialog().ok('Looking for Player', line1)
        #
        dictionnairedesPlayers[0]['count'] = nombredeplayers
        dictionnairedesPlayers[0]['Description'] = 'contient les players - le zero est réservé '

        xbmc.log('le super dico à la sortie : ' + str(dictionnairedesPlayers),xbmc.LOGDEBUG) # return example : {1: {}, 2: {}, 3: {}}
        '''
        example of dictionnairedesPlayers return : 
        [{'count': 3, 'Description': 'contient les players - le zero est r\xc3\xa9serv\xc3\xa9 '},
         {'modelname': 'SqueezeLite', 'uuid': '', 'power': '0', 'playerid': 'b8:27:eb:cf:f2:c0',
          'ip': '192.168.1.15:50102', 'canpoweroff': '1', 'firmware': 'v1.9.2-1158-pCP', 'displaytype': 'none',
          'playerindex': '0', 'seq_no': '0', 'connected': '1', 'isplayer': '1', 'model': 'squeezelite',
          'isplaying': '0', 'name': 'piCorePlayer'},
         {'modelname': 'Web Client', 'uuid': '', 'power': '1', 'playerid': '192.168.1.33', 'ip': '192.168.1.33:51064',
          'canpoweroff': '0', 'firmware': '', 'playerindex': '1', 'seq_no': '0', 'connected': '0', 'isplayer': '0',
          'model': 'http', 'isplaying': '1', 'name': 'Mozilla de 192.168.1.33'},
         {'modelname': 'Squeezebox Receiver', 'uuid': '21ec511edaa5a094fdb5301d7fa44c07', 'power': '0',
          'playerid': '00:04:20:17:1c:44', 'ip': '192.168.1.17:41620', 'canpoweroff': '1', 'displaytype': 'none',
          'playerindex': '2', 'seq_no': '0', 'connected': '1', 'isplayer': '1', 'model': 'receiver', 'isplaying': '0',
          'name': 'Squeezebox Receiver'}]
        '''
        self.dictionnairedesPlatines = dictionnairedesPlayers
        return dictionnairedesPlayers


    def playerActif(self, dictionnairedesPlayers ):
        '''
        recherche le player connecté et qui joue
        mais non pas bon -> en fait si connecté
        et si non actif passer par la fonction activeRplayer
        et si rien de jouer passer par la fonction jouerPlayer
        Todo : revoir une fois le player selectionnée dans le menu principal
        :param dictionnairedesPlayers:
        :return:
        '''
        xbmc.log('le super dico à l entrée de la fonction : ' + str(dictionnairedesPlayers),xbmc.LOGDEBUG)
        nombredeplayers = dictionnairedesPlayers[0]['count']
        xbmc.log('nbre : ' + str(nombredeplayers), xbmc.LOGNOTICE)
        for x in range (1, nombredeplayers + 1 ):
            xbmc.log('  player x est : ' + str(x), xbmc.LOGNOTICE)
            xbmc.log(str(dictionnairedesPlayers[x]['isplaying'] == '1'), xbmc.LOGDEBUG)
            xbmc.log(str(dictionnairedesPlayers[x]['connected'] == '1'), xbmc.LOGDEBUG)
            #if (dictionnairedesPlayers[x]['isplaying'] == '1'):
            if (dictionnairedesPlayers[x]['connected'] == '1'):
                # à revoir plutôt tester [ ' connected'] == '1' . vs 'isplaying' parce que sinon
                # return False et exit du programme n°36
                # à revoir pour s'effacer au bout d'un timeout
                #playerText = ['The active player is : ']
                #self.update_playerbox(playerText)
                #playerText.append(dictionnairedesPlayers[x]['playerid'])
                #self.update_playerbox(playerText)
                #playerText.append( self.dictionnairedesplayers[x]['name'])  # sometime : player_name
                #self.update_playerbox(playerText)
                xbmc.log(str(dictionnairedesPlayers[x]['isplaying'] == '1'), xbmc.LOGDEBUG)
                xbmc.log(str(dictionnairedesPlayers[x]['connected'] == '1'), xbmc.LOGDEBUG)
                self.unplayeractif = dictionnairedesPlayers[x]['playerid']
                return ( True , x , dictionnairedesPlayers[x]['playerid'])
        return (False, x , dictionnairedesPlayers[(random.randint(1,nombredeplayers))]['playerid']) # return whatever if no one actif

    def get_unplayeractif(self):
        xbmc.log('request of one player :  ' + str(self.unplayeractif) ,xbmc.LOGNOTICE)
        if self.playerSelection:
            # this one must be selected by the user in the beginning of the program
            return self.playerSelection
        else:   # in case the player selected is empty we return an other one.
                # this case must not happen, but we never know a wrong program....
            return self.unplayeractif

    def activerPlayer(self):
        '''
        lorsque le player est power off [ 'power'] == 0
        fontion qui permet de rendre actif le player (passe à '1')
        todo
        :return:
        '''
        pass


 ##############################################################################
    # Convert number of seconds to summat nice for screen 00:00 etc
    # from Xsqueeze

def parse_duration(durationobj): #
    '''
    get from plugin audio squeezebox :
        lms is a mess with typing,
        I've seen the duration being returned as string, float and int
        This will try to parse the result from LMS into a int
    '''
    result = 0
    try:
        result = int(durationobj)
    except ValueError:
        try:
            result = float(durationobj)
            result = int(result)
        except ValueError:
            xbmc.log("Error parsing track duration" + str(durationobj), xbmc.LOGNOTICE)
    return result


#def getInHMS(self,secondes):
def getInHMS(secondes):
    '''
    original from squeezeplay
    local function _secondsToString(seconds)
        local hrs = math.floor(seconds / 3600)
        local min = math.floor((seconds / 60) - (hrs*60))
        local sec = math.floor( seconds - (hrs*3600) - (min*60) )

        if hrs > 0 then
            return string.format("%d:%02d:%02d", hrs, min, sec)
        else
            return string.format("%d:%02d", min, sec)
        end
    end
    this implementation below comes from Xsqueeze. Is it right ?
    :param secondes:
    :return:
    '''
    seconds = parse_duration(secondes)
    hours = seconds / 3600
    seconds -= 3600 * hours
    minutes = seconds / 60
    seconds -= 60 * minutes
    if hours == 0:
        return "%02d:%02d" % (minutes, seconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)



##############################################################################


def analysedecodage( trame ):
    '''
    fonction qui traite les encodages des trames reçues du serveur
    retourne une trame propre que l'on peut splitter
    :param self:
    :param trame:
    :return:
    '''
    trame = trame.replace('\r\n', '')
    listeA = trame.split(' ')  # changement des espaces temporairement pour encoder
    textA = '|'.join(listeA)  #
    textB = urllib.unquote(textA)  # on encode les caractères escape du web
    return textB

def recherchonsleServeur(self):

    self.rechercheduserveur = WhereIsTheLMSServer()
    if self.rechercheduserveur.RequeteExploratoire():

        #informationText.append('nom du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSnom))
        #self.update_textbox(informationText)
        xbmc.log("Type LMSnom : " + str(type(self.rechercheduserveur.LMSnom)), xbmc.LOGDEBUG)
        #informationText.append('UUID du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSUUID))
        xbmc.log("Type LMSUUID : " + str(type(self.rechercheduserveur.LMSUUID)), xbmc.LOGDEBUG)
        #self.update_textbox(informationText)
        #informationText.append('version du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSversion))
        xbmc.log("Type LMSversion : " + str(type(self.rechercheduserveur.LMSversion)), xbmc.LOGDEBUG)
        #self.update_textbox(informationText)
        # informationText.append('Répetition - Version du LMS : %(LMSversion)s ' % (self.rechercheduserveur.LMSversion))
        #self.update_textbox(informationText)
        #informationText.append('port web du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSwebport))
        xbmc.log("Type LMSwebport : " + str(type(self.rechercheduserveur.LMSwebport)), xbmc.LOGDEBUG)
        #self.update_textbox(informationText)
        #informationText.append('ip du CLI du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSCLIip))
        xbmc.log("Type LMSCLIip : " + str(type(self.rechercheduserveur.LMSCLIip)), xbmc.LOGDEBUG)
        #self.update_textbox(informationText)
        #informationText.append('port du CLI du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSCLIport))
        xbmc.log("Type LMSCLIport : " + str(type(self.rechercheduserveur.LMSCLIport)), xbmc.LOGDEBUG)
        #self.update_textbox(informationText)
        #informationText.append("End scanning Network. Continue ...")
        #self.update_textbox(informationText)
        # need to retrieve cover jpg
        self.lmsip = self.rechercheduserveur.LMSCLIip
        self.lmswebport = self.rechercheduserveur.LMSwebport
        #ne fonctionne pas comme je l'espérais
        #self.rechercheduserveur.DonnonsAMangerAKodi()

        line0 = "Running scan on Network..."
        line1 = 'nom du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSnom) + '\n' + \
                'UUID du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSUUID) + '\n' +\
                'version du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSversion) + '\n' +\
                'port web du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSwebport) + '\n' +\
                'ip du CLI du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSCLIip) + '\n' + \
                'port du CLI du LogitechMediaServeur : ' + str(self.rechercheduserveur.LMSCLIport) + '\n'
        line7 = "End scanning Network. Continue ..."

        # todo : désactiver pour passer directement
        xbmcgui.Dialog().ok('Network Discovery', line1 )

    else:
        line0 = "Running scan on Network..."
        line1 = 'Fail ... no server found'
        line7 = "End scanning Network. Exit ...Error N° 32"
        xbmcgui.Dialog().ok('Network Discovery', line1, line7 )

        #informationText.append('Fail ... no server found')
        #self.update_textbox(informationText)
        xbmc.Monitor().waitForAbort(1)
        self.stop()
        exit(32)
    return





# procédure de test 
if __name__ == '__main__':
    Kodi = False
    print ('++++++++++je demarre++++++++++')
    testdureseau = WhereIsTheLMSServer()
    testdureseau.RequeteExploratoire()
    #testdesplayers = WhatAreThePlayers()
    #...testdesplayers.listePlayers ...

    # testdureseau.Ecoute()
    print ("it's done")

