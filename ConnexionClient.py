#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''


'''

import socket
import threading
import time
import urllib
import inspect

global Kodi
Kodi = True
if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct

#from singleton_decorator import singleton
def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper



@singleton
class InterfaceCLIduLMS(threading.Thread):


    dataExchange =''
    terminator ='\r\n'
    recevoirEnAttente = threading.Event()
    demandedeStop = threading.Event()

    def __init__(self, LMSCLIip, recevoirEnAttente , envoiEnAttente , demandedeStop):
        """

        :type evenement: threading.Event
        """
        threading.Thread.__init__(self)
        self.EtatDuThread = False
        self.demandedeStop = demandedeStop
        self.demandedeStop.clear()
        self.recevoirEnAttente = recevoirEnAttente
        self.envoiEnAttente = envoiEnAttente
        self.LMSCLIport=9090
        self.LMSCLIip = LMSCLIip
        self.socketdeConnexion = None
        # important here is the terminator string to all the request
        # terminator = '\r\n' # to remember but put by the function sendtoCLIsome...()
        self.terminator = '\r\n'
        self.recu = b''
        self.dataExchange = ''


    def run(self):
        xbmc.log('lancement de la connexion' , xbmc.LOGNOTICE)
        #création du socket
        self.connecttoCLI(self.LMSCLIip,self.LMSCLIport)

        message = "login" + self.terminator
        try:
            self.socketdeConnexion.send(bytes(message, 'ascii'))
        except TypeError:
            self.socketdeConnexion.send(bytes(message))
        time.sleep(0.2)
        self.recevoirEnAttente.clear()
        ReponseACK = self._receiveFromCLISomething()
        if ReponseACK == b'login ******\x0d\x0a':
            xbmc.log(" connexion ! , bonne reponse du serveur : " + ReponseACK.decode() , xbmc.LOGNOTICE)
            self.EtatDuThread = True
        else:
            xbmc.log("no connect, Echec !!!", xbmc.LOGNOTICE)
            # il faudrait prévenir le lanceur qu'il atennde pas pour rien !!
            # revoir la logique
            self.EtatDuThread = False


        while not self.demandedeStop.is_set():      # boucle infinie jusqu'à demande d'arrêt par le prog principal
            self.SignalAUnConsommateurDataRecu()    # dans cette boucle juste un signal que des données sont recues
            #time.sleep(0.1)                         # et à lire par le consommateur

        #self._closeconnexionWithCLI()
        #xbmc.log('closeconnexionwithCLI', xbmc.LOGNOTICE)
        #self.EtatDuThread = False
    # fin run


    def connecttoCLI(self, host, port):
        self.LMSCLIip = host
        self.LMSCLIport = port
        self.socketdeConnexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        verif = self.socketdeConnexion.connect((self.LMSCLIip, self.LMSCLIport))
        xbmc.log( ' socket créé : ' + str(verif) , xbmc.LOGNOTICE )
        xbmc.log("connecté au serveur " + self.LMSCLIip + " sur l interface CLI ? : " + str(verif) , xbmc.LOGNOTICE)

    def sendtoCLISomething(self, message):
        message += self.terminator
        try:
            message = bytes(message,'ascii')
        except TypeError:
            message = bytes(message)
        totalsent = 0
        sent = self.socketdeConnexion.send(message[totalsent:])
        totalsent = totalsent + sent
        self.envoiEnAttente.clear()
        xbmc.log("nbre d'octets envoyes : " +  str(totalsent) , xbmc.LOGNOTICE)
        xbmc.log( ' envoi de : ' + str(message) , xbmc.LOGNOTICE)

    def _receiveFromCLISomething(self):
        '''
        better if you don't call it outside the class
        because of the state of event is not set
        prefer the passeAUnConsommateur...()
        :return:
        '''
        chunks = []
        bytes_recd = 0
        chunk = self.socketdeConnexion.recv(32768)   # atatention si reset connexion -> bug faire un try todo
        # taille buffer was 2048 not enougth ?8192 ?
        xbmc.log(b'reponse brute du serveur LMS : ' + chunk , xbmc.LOGDEBUG)
        return chunk

    def SignalAUnConsommateurDataRecu(self):
        '''
        fonction qui signale au besoin que des données sont prêtes
        Dans les premières versions on traitait le decodage ici
        mais il faut laisser les données brutes et les laisser traiter
        par l'appelant
        :return:
        '''
        # todo à tester les deux versions
        self.dataExchange = self._receiveFromCLISomething()
        #self.dataExchange = self.dataExchange + self._receiveFromCLISomething()
        self.recevoirEnAttente.set()
        return  # cette fois en string !!

    def _closeconnexionWithCLI(self):
        #self.socketdeConnexion.unlink()
        self.socketdeConnexion.shutdown(socket.SHUT_RDWR)
        self.socketdeConnexion.close()
        del self.socketdeConnexion
        self.EtatDuThread = False

    def closeconnexionWithCLI(self):
        xbmc.log('Demande de fermeture de la connexion : ' + str(inspect.currentframe() ) , xbmc.LOGNOTICE)
        self.demandedeStop.set()
        self._closeconnexionWithCLI()

    def pluginCommandsAndQueries(self, plugin, start, nbre_par_reponse,  params ):
        #<radios|apps> <start> <itemsPerResponse> <taggedParameters>
        self.sendtoCLISomething(plugin + ' ' + start + ' ' +  nbre_par_reponse + ' ' + params + ' ')

    def receptionReponseEtDecodage(self): # à tester
        self.recevoirEnAttente.wait()  # le time est grand car selon la taille la réponse peut tarder
        recu_ext = self.dataExchange
        self.dataExchange = ''
        self.recevoirEnAttente.clear()
        trame = recu_ext.replace('\r\n', '')
        listeA = trame.split(' ')  # changement des espaces temporairement pour encoder
        textA = '|'.join(listeA)  #
        trame_decode = urllib.unquote(textA)  # on encode les caractères escape du web
        xbmc.log('trame récue décodée : ' + trame_decode, xbmc.LOGNOTICE)
        return trame_decode # trame sans les encodages web et avec séparateur espace changé pour '|'

    def receptionReponseEtDecodageavecCR(self): # à tester
        self.recevoirEnAttente.wait()  # le time est grand car selon la taille la réponse peut tarder
        recu_ext = self.dataExchange
        self.dataExchange = ''
        self.recevoirEnAttente.clear()
        #trame = recu_ext.replace('\r\n', '')
        listeA = recu_ext.split(' ')  # changement des espaces temporairement pour encoder
        textA = '|'.join(listeA)  #
        trame_decode = urllib.unquote(textA)  # on encode les caractères escape du web
        xbmc.log('trame récue décodée : ' + trame_decode, xbmc.LOGNOTICE)
        return trame_decode # trame sans les encodages web et avec séparateur espace changé pour '|'