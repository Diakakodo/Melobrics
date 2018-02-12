"""Gère l'enregistrement et l'affichage des meilleurs scores dans une fenêtre"""


import sys                          # pour obtenir le chemin du jeu
import os.path                      # pour les opérations sur les chemins
from tkinter import *               # pour les widgets


# On récupère le chemin du dossier du jeu, pour y écrire le fichier des scores
#   __file__ est le chemin du fichier python, dirname en extrait le dossier du jeu,
#   os.sep est le séparateur de chemins du système ("\" dans C:\windows\ par exemple)
_CHEMIN_FICHIER_SCORES = os.path.dirname(__file__) + os.sep + "scores.txt"
# le résultat est donc : "C:\<chemin_du_jeu>\scores.txt"


class FenetreScores(Tk):
    """Fenêtre qui enregistre et affiche les scores"""
    
    def __init__(self, difficulte_max):
        """Crée les widgets et les place dans la fenêtre"""
        
        # constructeur de la classe parent Tk
        super().__init__()
        
        # titre et taille de la fenêtre
        self.wm_title("Meilleurs scores")
        self.resizable(width=False, height=False)

        # on enregistre la difficulté maximale
        self.difficulte_max = difficulte_max
        
        # la fenêtre est masquée par défaut et se masque quand on la ferme
        self.withdraw()                                     # withdraw masque la fenêtre
        self.protocol("WM_DELETE_WINDOW", self.withdraw)    # fermer la fenêtre = la masquer
        
        # création des widgets
        self.tableau_scores = Listbox(self, width=50, height=30)
        self.tableau_scores.pack(side=LEFT)
        self.panneau_boutons = Frame(self)
        self.boutons_difficultes = []
        class BoutonDifficulte(Button):
            """Bouton changeant la difficulté affichée dans le panneau"""
            def __init__(self, parent, liste_boutons, action, difficulte):
                super().__init__(parent, text="Difficulté {}".format(difficulte))
                self.liste_boutons=liste_boutons
                self.action=action
                self.difficulte=difficulte
                self.config(command=self.clic)
            def clic(self):
                self.config(relief=SUNKEN)
                for bouton in self.liste_boutons:
                    if bouton != self:
                        bouton.config(relief=RAISED)
                self.action(self.difficulte)
        for difficulte in range(1, self.difficulte_max+1):
            bouton = BoutonDifficulte(self.panneau_boutons, self.boutons_difficultes, self.afficherDifficulte, difficulte)
            self.boutons_difficultes.append(bouton)
            bouton.pack()
            
        self.separateur = Frame(self.panneau_boutons, width=30, height=30)
        self.separateur.pack()
        self.boutonQuitter = Button(self.panneau_boutons, text="Fermer", command=self.withdraw)
        self.boutonQuitter.pack()
        self.panneau_boutons.pack(side=LEFT)

        # on affiche la difficulté 1 par défaut
        self.tableau_scores.difficulte_affichee = 1
        self.boutons_difficultes[0].config(relief=SUNKEN)
        
        # fichier des scores
        self.fichier = open(_CHEMIN_FICHIER_SCORES, "a+", encoding="utf-8")
        self.lireScores()

    def afficherDifficulte(self, difficulte):
        """Affiche les scores de la difficulté demandée dans le tableau"""

        self.tableau_scores.difficulte_affichee = difficulte
        self.actualiserWidgets()
        
    def ajouterScore(self, pseudo, score, difficulte):
        """Ajoute un score à la liste"""

        self.scores_par_difficulte[difficulte-1].append((score, pseudo))

        self.scores_par_difficulte[difficulte-1].sort()
        self.scores_par_difficulte[difficulte-1].reverse()
        
        self.actualiserWidgets()
    
    def lireScores(self):
        """Lit le fichier et met à jour les scores affichés par la fenêtre"""

        self.scores_par_difficulte = [[] for i in range(self.difficulte_max)]   # on efface l'ancienne liste
        
        self.fichier.seek(0)                                                    # on se place au début du fichier
        for ligne in self.fichier.readlines():                                          # Pour chaque ligne du fichier,
            score = ligne[:-1].split(":")                                               # on sépare la ligne selon le format des scores (pseudo:score:difficulté),
            if len(score) != 3 or not score[1].isdigit() or not score[2].isdigit():     # s'il n'y a pas trois parties séparées par ':' ou si score ou difficulté n'est pas un nombre,
                continue                                                                # on ignore la ligne. Sinon,
            self.ajouterScore(score[0], int(score[1]), int(score[2]))                   # on enregistre le score.
    
    def actualiserWidgets(self):
        """Met à jour les scores affichés par la fenêtre"""
        
        self.tableau_scores.delete(0, END)
        
        for score in self.scores_par_difficulte[self.tableau_scores.difficulte_affichee-1]:
            self.tableau_scores.insert(END, "{} : {}".format(score[1], score[0]))
    
    def ecrireScores(self):
        """Ecrit la liste actuelle des scores dans le fichier"""
        
        self.fichier.truncate(0)
        self.fichier.write("Fichier des scores. Format : \"<pseudo>:<score>:<difficulté>\".\nAttention, les lignes ne respectant pas ce format seront ignorées lors de la lecture et disparaîtront lors de la réécriture du fichier.\n\n")
        
        for difficulte in range(self.difficulte_max):
            for score in self.scores_par_difficulte[difficulte]:
                self.fichier.write("{}:{}:{}\n".format(
                    score[1],
                    score[0],
                    difficulte+1))
    
    def destroy(self):
        """Ecrit les scores dans le fichier et ferme ce dernier avant de quitter"""
        
        self.ecrireScores()     # on écrit les scores dans le fichier
        self.fichier.close()    # on ferme le fichier

        super().destroy()       # on détruit la fenêtre

