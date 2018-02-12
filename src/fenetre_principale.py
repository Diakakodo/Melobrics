"""Fenêtre principale du jeu ; transmet les commandes à GrilleMelobrics et gère l'agencement des widgets"""

from tkinter.messagebox import *  # pour les boîtes de dialogue
from tkinter.simpledialog import askstring  # pour le nom

from grille import *  # pour le widget affichant la grille

from fenetre_scores import *  # pour la fenêtre des meilleurs scores

# nombre de colonnes et de lignes de la grille
_NBCOLONNES_DEFAUT  = 10
_NBLIGNES_DEFAUT    = 15

# taille du canvas des contrôles en pixels
_LARGEUR_PANNEAUCONTROLES = 200
_HAUTEUR_PANNEAUCONTROLES = 675

# taille du widget "prochaine pièce" en pixels
_LARGEUR_PROCHAINEPIECE = 75
_HAUTEUR_PROCHAINEPIECE = 100

# difficulté maximale
_DIFFICULTE_MAX = 10


class FenetrePrincipale(Tk):
    """Fenetre principale"""

    def __init__(self):
        """Crée les widgets et affiche l'écran d'accueil"""

        # constructeur de la classe parent Tk
        super(FenetrePrincipale, self).__init__()

        # titre et taille de la fenêtre
        self.wm_title("Mélobrics")
        self.resizable(width=False, height=False)
        largeur_ecran, hauteur_ecran = self.winfo_screenwidth(), self.winfo_screenheight()

        # on crée les deux grands cadres de la fenêtre : 
        # - la grille de jeu,
        self.canvasGrille = GrilleMelobrics(    # paramètres de la grille :
            self,                               # - widget parent (la fenêtre)
            largeur_ecran*0.3,                  # - largeur en pixels
            largeur_ecran*0.3/10*15,            # - hauteur en pixels
            _NBCOLONNES_DEFAUT,                 # - nombre de colonnes
            _NBLIGNES_DEFAUT,                   # - nombre de lignes
            self.rappelNouvellePartie,          # - fonction appelée lors d'une nouvelle partie
            self.rappelProchainePieceChange,    # - fonction appelée quand la prochaine pièce change
            self.rappelPauseChange,             # - fonction appelée quand la pause est (dés)activée
            self.rappelScoreChange,             # - fonction appelée quand le score change
            self.rappelPartieTerminee           # - fonction appelée quand la partie est terminée
        )
        # - le panneau des contrôles.
        self.panneauControles = Frame(self, width=largeur_ecran*0.15, height=largeur_ecran*0.3/10*15)
        self.panneauControles.pack_propagate(False) # empêche le cadre de se redimensionner
        
        # on crée la fenêtre des meilleurs scores
        self.fenetreScores = FenetreScores(_DIFFICULTE_MAX)

        # on crée les contrôles dans le panneauControles
        def nouvellePartie():
            self.canvasGrille.nouvellePartie(self.curseurDifficulte.get(), self.limiterScore.get())
        def abandonner():
            self.canvasGrille.partieTerminee(False)
        def changerPause():
            self.canvasGrille.changerPause()
        def meilleursScores():
            self.fenetreScores.deiconify()
        self.canvasProchainePiece = CanvasPiece(self.panneauControles, _LARGEUR_PROCHAINEPIECE, _HAUTEUR_PROCHAINEPIECE)
        self.labelScore = Label(self.panneauControles)
        self.boutonNouvellePartie = Button(self.panneauControles, text="Nouvelle partie", command=nouvellePartie)
        self.boutonMeilleursScores = Button(self.panneauControles, text="Meilleurs scores", command=meilleursScores)
        self.boutonAbandonner = Button(self.panneauControles, text="Abandonner", command=abandonner)
        self.boutonPause = Button(self.panneauControles, text="Lancer !", command=changerPause)
        self.boutonAide = Button(self.panneauControles, text="Comment jouer ?", command=self.afficherAide)
        self.boutonQuitter = Button(self.panneauControles, text="Quitter", command=self.destroy)
        self.cadreDifficulte = Frame(self.panneauControles)
        self.labelDifficulte = Label(self.cadreDifficulte, text="Difficulté : ")
        self.labelDifficulte.pack(side=LEFT)
        self.curseurDifficulte = Scale(self.cadreDifficulte, from_=1, to=_DIFFICULTE_MAX, orient=HORIZONTAL)
        self.curseurDifficulte.pack(side=LEFT)
        self.limiterScore = BooleanVar()
        self.caseLimiterScore = Checkbutton(self.panneauControles, text="Limiter le score", variable=self.limiterScore)
        # séparateurs pour améliorer le placement des widgets
        self.separateurs_30px = [Frame(self.panneauControles, width=30, height=30) for i in range(3)]
        self.separateurs_5px = [Frame(self.panneauControles, width=5, height=5) for i in range(5)]

        # sélectionner un bouton avec Tab provoque un conflit avec la touche Espace, on désactive donc Tab
        def neRienFaire(evenement):
            return "break"      # demande d'ignorer l'événement (l'appui de la touche ne sera pas traité)
        self.bind("<Tab>", neRienFaire)    # on affecte à Tab une fonction qui ne fait rien

        # on affiche l'accueil
        self.afficherEcranAccueil()

    def afficherAide(self, event=None):
        """Affiche l'aide du jeu"""

        # On évite de laisser le jeu tourner derrière la fenêtre d'aide
        self.canvasGrille.changerPause(True)

        # Puis on affiche la boîte de dialogue d'aide
        showinfo("Comment jouer",
                "Les contrôles sont simples :\n- flèches droite et gauche pour dévier la pièce\n- flèche bas pour descendre plus vite\n- flèche haut pour retourner la pièce\n- espace pour activer et désactiver la pause\n\n(astuce : supprimer plusieurs lignes d'un coup rapporte plus de points !)")

    def rappelNouvellePartie(self):
        """Change l'affichage pour une nouvelle partie"""

        self.boutonPause.config(text="Lancer !")    # On change le texte du bouton Pause,
        self.afficherEcranJeu()                     # puis on affiche l'écran de jeu.

    def rappelPauseChange(self, enPause):
        """Met à jour l'affichage si le jeu passe en pause ou se relance"""

        # On change le texte du bouton pause.
        if enPause:
            self.boutonPause.config(text="Reprendre")
        else:
            self.boutonPause.config(text="Pause")

    def rappelProchainePieceChange(self, prochainePiece):
        """Met à jour le canvasProchainePiece"""

        self.canvasProchainePiece.changerPiece(prochainePiece)

    def rappelScoreChange(self, score, limiterScore, scoreMaximal):
        """Met à jour l'affichage du score"""

        # On crée la chaîne qui sera affichée dans le Label...
        self.texteScore = str(score)
        if limiterScore:                                    # si le score est limité,
            self.texteScore += "/{}".format(scoreMaximal)   # on affiche aussi le score maximal

        # ...puis on met à jour le Label.
        self.labelScore.config(text="Score : " + self.texteScore)

    def rappelPartieTerminee(self, score, difficulte, gagne=False):
        """Informe le joueur que la partie est terminée en donnant son score, propose d'enregistrer le score, retourne à l'accueil"""

        # On informe le joueur
        # (self.textScore est défini dans FenetrePrincipale.scoreChange)
        if gagne:
            sauverScore = askyesno("Gagné", "Félicitations, vous avez gagné ! :)\nVotre score est de {}.\n\nVoulez-vous enregistrer ce score ?".format(self.texteScore))
        else:
            sauverScore = askyesno("Perdu", "Vous avez perdu :(\nVotre score est de {}.\n\nVoulez-vous enregistrer ce score ?".format(self.texteScore))
        
        if sauverScore: # s'il veut enregistrer son score,
            while True: # on lui demande un nom en boucle, jusqu'à ce qu'il soit valide
                pseudo = askstring("Nouveau score", "Entrez votre nom :")
                if pseudo == None:
                    break
                elif pseudo == "":                  # si le nom est vide
                    showerror("Nom vide", "Veuillez entrer un nom.")
                elif ":" in pseudo:                 # si le nom contient ":"
                    showerror("Nom invalide", "Le nom ne peut pas contenir le caractère ':'.")
                else:                               # si le nom est correct
                    self.fenetreScores.ajouterScore(pseudo, score, difficulte)
                    break

        # on revient à l'écran d'accueil.
        self.afficherEcranAccueil()

    def afficherEcranAccueil(self):
        """Affiche l'écran d'accueil"""

        # On masque l'écran précédent...
        self.cacherEcranPrecedent()

        # ...on place les contrôles dans le panneauControles...
        self.separateurs_30px[0].pack()
        self.separateurs_30px[1].pack()
        self.boutonNouvellePartie.pack()
        self.separateurs_5px[0].pack()
        self.boutonMeilleursScores.pack()
        self.separateurs_5px[1].pack()
        self.cadreDifficulte.pack()
        self.separateurs_5px[2].pack()
        self.caseLimiterScore.pack()
        self.separateurs_5px[3].pack()
        self.boutonAide.pack()
        self.separateurs_5px[4].pack()
        self.boutonQuitter.pack()
        
        # ...puis les deux grands cadres (canvasGrille et panneauControles) dans la fenêtre.
        self.canvasGrille.pack(side=LEFT)
        self.panneauControles.pack(side=LEFT)

    def afficherEcranJeu(self):
        """Affiche l'écran de jeu et affecte les touches du clavier aux contrôles"""

        # On masque l'écran précédent...
        self.cacherEcranPrecedent()

        # ...on place les contrôles dans le panneauControles...
        self.separateurs_30px[0].pack()
        self.separateurs_30px[1].pack()
        self.canvasProchainePiece.pack()
        self.labelScore.pack()
        self.separateurs_30px[2].pack()
        self.boutonPause.pack()
        self.separateurs_5px[0].pack()
        self.boutonAbandonner.pack()
        self.separateurs_5px[1].pack()
        self.boutonAide.pack()
        self.separateurs_5px[2].pack()
        self.boutonQuitter.pack()
        
        # ...puis les deux grands cadres (canvasGrille et panneauControles) dans la fenêtre...
        self.canvasGrille.pack(side=LEFT)
        self.panneauControles.pack(side=LEFT)

        # ...et on affecte les touches.
        def changerPause(evenement):
            self.canvasGrille.changerPause()
        self.bind("<space>", changerPause)
        self.bind("<Right>", self.canvasGrille.mouvementDroite)
        self.bind("<Left>", self.canvasGrille.mouvementGauche)
        self.bind("<Down>", self.canvasGrille.mouvementBas)
        self.bind("<Up>", self.canvasGrille.retournerPiece)

    def cacherEcranPrecedent(self):
        """Retire tous les widgets de la fenêtre et désaffecte toutes les touches clavier.
           A appeler avant de chaner d'écran."""

        # On masque tous les widgets...
        for widget in (self.winfo_children() + self.panneauControles.winfo_children()): # winfo_children renvoie la liste des widgets
            widget.pack_forget()

        # ...et on désaffecte toutes les touches.
        self.unbind("<space>")
        self.unbind("<Right>")
        self.unbind("<Left>")
        self.unbind("<Down>")
        self.unbind("<Up>")
        
    def destroy(self):
        """Détruit la fenêtre des scores avant de détruire la fenêtre principale"""
        
        self.fenetreScores.destroy()
        super().destroy()

