#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
first version with socket
second version (this one) with TelnetLib

'''

import threading
import time
import urllib
import inspect
import sys
import telnetlib

global Kodi
Kodi = True
if Kodi:
    import xbmc
    import xbmcgui
    import xbmcaddon
    import pyxbmct

    DEBUG_LEVEL = xbmc.LOGDEBUG
    ADDON_ID ='script.kodijivelette'

def debug(message, level=DEBUG_LEVEL):
    """Basic debug function for outputting info to the log.
       get from script.squeezeinfo by elParaguayo

      Should not use anything higher than debug to avoid spamming the logfile.
    """
    # Make sure encoding is ok for log file
    if isinstance (message, str):
        message = message.decode("utf-8")

    # Format the message and send to the logfile
    message = u"{}: {}".format(ADDON_ID, message)
    xbmc.log(msg=message.encode("utf-8"), level=level)


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
        self.startDone = False
        self.connexionAuServeurReussie = False
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
        debug('lancement de la connexion' , xbmc.LOGNOTICE)
        #création du socket
        if self.connecttoCLI(self.LMSCLIip,self.LMSCLIport):
            #doublon
            self.connexionAuServeurReussie = True
            #self.socketdeConnexion.read_all()
            debug('ConnexionClient Reussie : ' + str(self.connexionAuServeurReussie)  , xbmc.LOGNOTICE)

            message = "login" + self.terminator
            try:
                #self.socketdeConnexion.send(bytes(message, 'ascii'))
                self.socketdeConnexion.write(message)
            except SocketError:
                debug(" Socket error !!!", xbmc.LOGNOTICE)
                self.EtatDuThread = False
                self.startDone = False
                self.connexionAuServeurReussie = False

            self.recevoirEnAttente.clear()
            ReponseACK = self._receiveFromCLISomething()
            if ReponseACK == b'login ******\x0d\x0a':
                debug(" connexion ! , bonne reponse du serveur : " + ReponseACK.decode() , xbmc.LOGNOTICE)
                self.EtatDuThread = True
                self.startDone = True
            else:
                debug("no connect, Echec !!!", xbmc.LOGNOTICE)
                # il faudrait prévenir le lanceur qu'il atennde pas pour rien !!
                # revoir la logique
                self.EtatDuThread = False
                self.startDone = True
        else:
            debug("creation socket refusé", xbmc.LOGNOTICE)
            self.EtatDuThread = False
            #doublon
            self.connexionAuServeurReussie = False
            self.startDone = True
            return

        self.EtatDuThread = True
        while not self.demandedeStop.is_set():      # boucle infinie jusqu'à demande d'arrêt par le prog principal
            self.SignalAUnConsommateurDataRecu()    # dans cette boucle juste un signal que des données sont recues
            #time.sleep(0.1)                         # et à lire par le consommateur

        #self._closeconnexionWithCLI()
        #debug('closeconnexionwithCLI', xbmc.LOGNOTICE)
        #self.EtatDuThread = False
    # fin run


    def connecttoCLI(self, host, port):
        self.LMSCLIip = host
        self.LMSCLIport = port
        try:
            self.socketdeConnexion = telnetlib.Telnet( self.LMSCLIip, self.LMSCLIport )
        except:
            # connecxion refusée ou bien ???
            debug('ConnecttoCLI : return False',xbmc.LOGNOTICE)
            self.connexionAuServeurReussie = False
            return False
        debug(' socket créé  ' , xbmc.LOGNOTICE)
        debug("connecté au serveur " + self.LMSCLIip + " sur l interface CLI  : " , xbmc.LOGNOTICE)
        debug('ConnecttoCLI : return True', xbmc.LOGNOTICE)
        self.connexionAuServeurReussie = True
        return True

    def sendtoCLISomething(self, message):
        message += self.terminator

        totalsent = 0
        try:
            self.socketdeConnexion.write(message)
        except:
            debug(" Socket error !!!", xbmc.LOGNOTICE)
            self.EtatDuThread = False
            self.startDone = False
            self.connexionAuServeurReussie = False
        #totalsent = totalsent + sent
        self.envoiEnAttente.clear()
        debug("nbre d'octets envoyes : " +  str(totalsent) , xbmc.LOGNOTICE)
        debug( ' envoi de : ' + str(message) , xbmc.LOGNOTICE)

    def _receiveFromCLISomething(self):
        '''
        better if you don't call it outside the class
        because of the state of event is not set
        prefer the passeAUnConsommateur...()
        :return:
        '''
        chunks = []
        bytes_recd = 0
        try:
            chunk = self.socketdeConnexion.read_until(self.terminator)   # Attention si reset connexion catch exception
        except:
            debug('Exception sur réponse du serveur', xbmc.LOGNOTICE)
        debug('reponse brute du serveur LMS : ' + chunk + '\n', xbmc.LOGDEBUG)
        debug('size of chunk : ' + str(len(chunk)) + '\n', xbmc.LOGDEBUG)
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
        debug('dataExchange waiting : ' + self.dataExchange + '\n', xbmc.LOGDEBUG)
        self.recevoirEnAttente.set()
        return

    def dataAreWaiting(self):
        if self.dataExchange == '':
            return False
        else:
            return True


    def _closeconnexionWithCLI(self):
        #self.socketdeConnexion.unlink()
        #self.socketdeConnexion.shutdown(socket.SHUT_RDWR)
        self.socketdeConnexion.write('exit')
        self.socketdeConnexion.close()
        del self.socketdeConnexion

    def closeconnexionWithCLI(self):
        debug('Demande de fermeture de la connexion : ' + str(inspect.currentframe() ) , xbmc.LOGNOTICE)
        self.demandedeStop.set()
        self._closeconnexionWithCLI()
        self.connexionAuServeurReussie = False
        self.EtatDuThread = False

    def pluginCommandsAndQueries(self, plugin, start, nbre_par_reponse,  params ):
        # not used , Todo Delete it
        #<radios|apps> <start> <itemsPerResponse> <taggedParameters>
        self.sendtoCLISomething(plugin + ' ' + start + ' ' +  nbre_par_reponse + ' ' + params + ' ')

    def receptionReponseEtDecodage(self): # à tester
        self.recevoirEnAttente.wait()
        recu_ext = self.dataExchange
        self.dataExchange = ''
        self.recevoirEnAttente.clear()
        trame = recu_ext.replace('\r\n', '')
        listeA = trame.split(' ')  # changement des espaces temporairement pour encoder
        textA = '|'.join(listeA)  #
        trame_decode = urllib.unquote(textA)  # on encode les caractères escape du web
        debug('trame décodée et espace substitué  : ' + trame_decode + '\n', xbmc.LOGNOTICE)
        return trame_decode # trame sans les encodages web et avec séparateur espace changé pour '|'

    def receptionReponseEtDecodageavecCR(self): # à tester
        self.recevoirEnAttente.wait()
        recu_ext = self.dataExchange
        self.dataExchange = ''
        self.recevoirEnAttente.clear()
        #trame = recu_ext.replace('\r\n', '')
        listeA = recu_ext.split(' ')  # changement des espaces temporairement pour encoder
        textA = '|'.join(listeA)  #
        trame_decode = urllib.unquote(textA)  # on encode les caractères escape du web
        debug('trame récue décodée : ' + trame_decode, xbmc.LOGNOTICE)
        return trame_decode # trame sans les encodages web et avec séparateur espace changé pour '|'

    def receptionReponseEtPoubelle(self):
        self.recevoirEnAttente.wait()  # le time est grand car selon la taille la réponse peut tarder
        recu_ext = self.dataExchange
        debug('trame recue brute : ' + recu_ext, xbmc.LOGNOTICE)
        del recu_ext
        self.dataExchange = ''
        self.recevoirEnAttente.clear()
        return

    def viderLeBuffer(self):
        #self.recevoirEnAttente.wait(0.1) or while self.recevoirEnAttente.is_set(): ?
        debug('trame détruite : ' + self.dataExchange , xbmc.LOGNOTICE)
        self.dataExchange = ''
        self.recevoirEnAttente.clear()
        return

    def sendSignal(self,commande):     # not yet used but should be
        self.dataExchange = commande
        self.recevoirEnAttente.set()
        debug('commande envoyée : ' + self.dataExchange , xbmc.LOGNOTICE)

