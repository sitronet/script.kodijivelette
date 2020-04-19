#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from ConnexionClient import InterFaceCliduLMS
import threading


import xbmc

TIME_OF_LOOP_SUBSCRIBE = '2' # initial 10 or 5 but long time to exit
                             # also delay for the refreshed duration playing


class Souscription(threading.Thread):
#class Souscription():

    def __init__(self, InterfaceCli, playerid ):
        """

        :type evenement: threading.Event
        """
        threading.Thread.__init__(self)
        self.InterfaceCLI = InterfaceCli
        self.playerid = playerid
        self.EtatDuThread = False
        # todo to check
        #self.recevoirEnAttente = recevoirEnAttente
        #self.Abonnement = Abonnement

        #self.envoiEnAttente = envoiEnAttente
        #self.LMSCLIport=9090
        #self.LMSCLIip = LMSCLIip
        #self.socketdeConnexion = None
        #self.terminator = '\r\n'
        self.recu = b''
        self.dataExchange = ''


    def timeofloopsubscribe(self):
        return TIME_OF_LOOP_SUBSCRIBE

    def subscription(self):
        # self.souscription(self.InterfaceCLI)
        ##############################################################################
        # avant d'entrer dans la boucle listen ou subscribe on envoie la requete
        # self.envoiEnAttente.wait(1)  # ne fonctionne pas comme je pense car le sendtoCLI ne remet jamais à zero !!!
        #self.InterfaceCLI.sendtoCLISomething(playerid + " status - 2 subscribe:30")  # bug si aucun player ne joue
        # self.InterfaceCLI.sendtoCLISomething(playerid + " status - 2 listen 1")
        xbmc.log("Souscription", xbmc.LOGNOTICE)
        self.InterfaceCLI.sendtoCLISomething(self.playerid + " status - 1 subscribe:" + TIME_OF_LOOP_SUBSCRIBE)

    def subscriptionLongue(self):
        xbmc.log("Souscription Longue", xbmc.LOGNOTICE)
        self.InterfaceCLI.sendtoCLISomething(self.playerid + " status 0 200 subscribe:" + TIME_OF_LOOP_SUBSCRIBE)

    def resiliersouscription(self):
        # Todo : define two methode : one with param - , other with 0
        self.InterfaceCLI.sendtoCLISomething(self.playerid + " status - 1 subscribe:- ")
        return

    def resilierSouscriptionWithoutAnswer(self):
        # function when don't need to check/analyse the server's answer
        self.resiliersouscription()
        self.InterfaceCLI.receptionReponseEtPoubelle()
        return

    def listen(self):
        xbmc.log("Listen 1 ", xbmc.LOGDEBUG)
        self.InterfaceCLI.sendtoCLISomething(self.playerid + " listen 1 ")
        reponse = self.InterfaceCLI.receptionReponseEtDecodage()
        if 'listen 1' in reponse:
            return True
        else:
            return False

    def resilierListen(self):
        xbmc.log("Listen 0 ", xbmc.LOGDEBUG)
        self.InterfaceCLI.sendtoCLISomething(self.playerid + " listen 0 ")
        #poubelle = self.InterfaceCLI.receptionReponseEtDecodage()
        del poubelle


