"""Widgets permettant de gérer et dessiner le jeu, et de traiter les commandes transmises par la fenêtre"""

from tkinter import *       # pour créer le widget affichant la grille
from random import randint  # pour choisir aléatoirement une forme et une couleur de pièce
from copy import deepcopy   # pour copier correctement une pièce


_PAS_SCORE = 100   # gain de score à chaque ligne détruite


# Liste des formes de pièces possibles
_FORMES_PIECES = (
    # ####
    [
        {
            "abscisse":1,
            "ordonnee":0
        },
        {
            "abscisse":0,
            "ordonnee":1
        },
        {
            "abscisse":1,
            "ordonnee":1
        },
        {
            "abscisse":2,
            "ordonnee":1
        },
    ],
    #  #
    # ###
    [
        {
            "abscisse":0,
            "ordonnee":0
        },
        {
            "abscisse":0,
            "ordonnee":1
        },
        {
            "abscisse":0,
            "ordonnee":2
        },
        {
            "abscisse":0,
            "ordonnee":3
        }
    ],
    # ##
    # ##
    [
        {
            "abscisse":0,
            "ordonnee":0
        },
        {
            "abscisse":1,
            "ordonnee":0
        },
        {
            "abscisse":0,
            "ordonnee":1
        },
        {
            "abscisse":1,
            "ordonnee":1
        },
    ],
    # #
    # ###
    [
        {
            "abscisse":0,
            "ordonnee":0
        },
        {
            "abscisse":0,
            "ordonnee":1
        },
        {
            "abscisse":1,
            "ordonnee":1
        },
        {
            "abscisse":2,
            "ordonnee":1
        },
    ],
    #   #
    # ###
    [
        {
            "abscisse":0,
            "ordonnee":1
        },
        {
            "abscisse":1,
            "ordonnee":1
        },
        {
            "abscisse":2,
            "ordonnee":1
        },
        {
            "abscisse":2,
            "ordonnee":0
        },
    ],
    #  ##
    # ##
    [
        {
            "abscisse":0,
            "ordonnee":1
        },
        {
            "abscisse":1,
            "ordonnee":1
        },
        {
            "abscisse":1,
            "ordonnee":0
        },
        {
            "abscisse":2,
            "ordonnee":0
        },
    ],
    # ##
    #  ##
    [
        {
            "abscisse":0,
            "ordonnee":0
        },
        {
            "abscisse":1,
            "ordonnee":0
        },
        {
            "abscisse":1,
            "ordonnee":1
        },
        {
            "abscisse":2,
            "ordonnee":1
        },
    ]
)

# Liste des couleurs de pièces possibles
_COULEURS_PIECES = (
    "blue",
    "green",
    "red",
    "orange",
    "purple",
    "yellow",
    "hotpink"
)


class _PieceMelobrics:
    """Représente une pièce (groupe de briques)"""

    def __init__(self, aleatoire=True, largeur=None, hauteur=None, couleur=None):
        """Si aleatoire=True, choisit aléatoirement les caractéristiques de la pièce
           Si aleatoire=False, crée une pièce vide, largeur, hauteur et couleur doivent être fournies

           Le cas aleatoire=False sert uniquement dans _PieceMelobrics.retourner"""

        if aleatoire == True:
            self.choisirAleatoirement()
        else:
            self.largeur, self.hauteur = largeur, hauteur
            self.couleur = couleur
            self.briques = list()

    def choisirAleatoirement(self):
        """Initialise aléatoirement forme et couleur de la pièce, à partir des listes au-dessus"""

        self.briques = _FORMES_PIECES[randint(0, len(_FORMES_PIECES)-1)]
        self.couleur = _COULEURS_PIECES[randint(0, len(_COULEURS_PIECES)-1)]

        self.largeur = 0
        self.hauteur = 0

        for brique in self.briques:
            brique["couleur"] = self.couleur
            self.largeur = max(self.largeur, brique["abscisse"]+1)
            self.hauteur = max(self.hauteur, brique["ordonnee"]+1)

    def ajouterBrique(self, abscisse, ordonnee):
        """Ajoute une brique dans la pièce aux coordonnées demandées"""

        self.briques.append({
                            "abscisse": abscisse,
                            "ordonnee": ordonnee,
                            "couleur": self.couleur
                        })

        self.largeur = max(self.largeur, abscisse+1)
        self.hauteur = max(self.hauteur, ordonnee+1)

    def retourner(self):
        """Renvoie la pièce retournée de 90°"""

        # on crée une pièce vide, qu'on remplira en parcourant la pièce à retourner (noter qu'on inverse hauteur et largeur)
        pieceRetournee = _PieceMelobrics(False, self.hauteur, self.largeur, self.couleur)

        # on copie chaque case de l'ancienne pièce à son nouvel emplacement
        for brique in self.briques:
            nouvelleAbscisse = pieceRetournee.largeur-1-brique["ordonnee"]
            nouvelleOrdonnee = brique["abscisse"]
            pieceRetournee.briques.append({
                                "abscisse": nouvelleAbscisse,
                                "ordonnee": nouvelleOrdonnee,
                                "couleur": self.couleur
                            })

            self.largeur = max(self.largeur, nouvelleAbscisse+1)
            self.hauteur = max(self.hauteur, nouvelleOrdonnee+1)

        return pieceRetournee


class GrilleMelobrics(Canvas):
    """Grille de jeu"""

    def __init__(self, maitre, largeur, hauteur, nbColonnes, nbLignes, rappelNouvellePartie, rappelNouvellePiece, rappelPause, rappelScoreChange, rappelPartieTerminee):
        """Initialise la grille.

        Liste des arguments :
        - maitre                    : fenêtre principale (passée au constructeur de Canvas)
        - largeur et hauteur        : taille en pixels de la grille (passée au constructeur de Canvas)
        - nbColonnes et nbLignes    : nombre de colonnes et de lignes de la grille
        - rappelNouvellePartie      : fonction appelée quand une nouvelle partie est prête
        - rappelNouvellePiece       : fonction appelée quand une nouvelle pièce est insérée (avec la prochainePiece en argument)
        - rappelPause               : fonction appelée quand le jeu entre ou sort de pause (avec self.enPause en argument)
        - rappelScoreChange         : fonction appelée quand le score change (avec le score en argument)
        - rappelPartieTerminee      : fonction appelée quand la partie est terminée (avec le score et la difficulté, et un argument : True si gagné, False sinon)

        La grille prévient la fenêtre principale avec les fonctions rappel<QuelqueChose> dès que quelqueChose a changé et a besoin d'être affiché.
        """

        # constructeur de la classe parent Canvas
        super().__init__(maitre, width=largeur, height=hauteur)

        # on ajoute à la grille une bordure noire
        self.config(borderwidth = 1, highlightbackground="black")

        # enregistrement des paramètres : taille de la grille, fonctions de rappel
        self.nbColonnes, self.nbLignes = nbColonnes, nbLignes
        self.rappelNouvellePartie = rappelNouvellePartie
        self.rappelNouvellePiece = rappelNouvellePiece
        self.rappelPause = rappelPause
        self.rappelScoreChange = rappelScoreChange
        self.rappelPartieTerminee = rappelPartieTerminee

        # initialisation : le jeu commence en pause et la pièce en déplacement n'est pas encore créée
        self.enPause = True
        self.piece = None

    def mouvementBas(self, evenement=None):
        """Fait avancer le jeu :
            - déplace la pièce d'un rang vers le bas si possible,
            - en insère une nouvelle si nécessaire,
            - pour chaque ligne pleine, efface la ligne et augmente le score,
            - se relance pour la prochaine étape"""

        if self.enPause:        # si le jeu est en pause,
            return              # on quitte

        # si une pièce est en mouvement, on tente de la faire descendre
        if self.piece != None:
            obstacle = False
            # on vérifie si la pièce a atteint la dernière ligne...
            if self.ordonneePiece >= self.nbLignes-self.piece.hauteur:
                obstacle = True
            # ...puis si elle a atteint un obstacle (une autre brique)
            else:
                for brique in self.piece.briques:
                    if self.grille[self.abscissePiece+brique["abscisse"]][self.ordonneePiece+brique["ordonnee"]+1] != None:
                        obstacle = True
                        break
            if obstacle:                            # Si la pièce est bloquée,
                for brique in self.piece.briques:   # on la "fixe" dans la grille,
                    self.grille[self.abscissePiece+brique["abscisse"]][self.ordonneePiece+brique["ordonnee"]] = brique
                self.piece = None                   # on la supprime,
                nb_lignes_pleines = 0
                for ligne in range(self.nbLignes):  # et on vérifie si des lignes sont remplies.
                    lignePleine = True
                    for colonne in range(self.nbColonnes):
                        if self.grille[colonne][ligne] == None:     # si une case est vide,
                            lignePleine = False                     # la ligne n'est pas pleine
                            break
                    # si la ligne est pleine, on la supprime et on augmente le score
                    if lignePleine:
                        # on augmente le score...
                        nb_lignes_pleines += 1
                        # le gain de score de chaque ligne est multiplié par le nombre de lignes détruites
                        # -> supprimer plusieurs lignes d'un coup peut rapporter beaucoup plus
                        self.score += _PAS_SCORE * nb_lignes_pleines
                        self.rappelScoreChange(self.score, self.limiterScore, self.scoreMaximal)
                        # ...on supprime la ligne...
                        for colonne in range(self.nbColonnes):
                            self.grille[colonne][ligne] = None
                        # ...on descend d'un rang toutes les lignes supérieures...
                        for ligne2 in range(1, ligne+1)[::-1]:
                            for colonne in range(self.nbColonnes):
                                self.grille[colonne][ligne2] = self.grille[colonne][ligne2-1]
                        # ...et si le score maximal est atteint, on a gagné
                        if self.limiterScore and self.score >= self.scoreMaximal:
                            self.partieTerminee(True)
                            return
            else:                                   # Si la pièce peut encore descendre,
                self.ordonneePiece += 1             # on la descend,

        # s'il n'y a pas ou plus de pièce en mouvement, on insère la suivante
        if self.piece == None:
            self.piece = deepcopy(self.prochainePiece)
            self.abscissePiece, self.ordonneePiece = self.nbColonnes//2 - self.piece.largeur//2, 0  # on change les coordonnées
            # on vérifie que la pièce peut être insérée
            obstacle = False
            for brique in self.piece.briques:                                                                       # pour chaque brique,
                if self.grille[self.abscissePiece+brique["abscisse"]][self.ordonneePiece+brique["ordonnee"]] != None:   # si la pièce ne peut pas être insérée,
                    self.partieTerminee(False)                                                                      # on a perdu
                    return
            self.prochainePiece = _PieceMelobrics()         # on crée la pièce suivante
            self.rappelNouvellePiece(self.prochainePiece)   # et on l'affiche

        # on redessine
        self.dessiner()

        if evenement != None:                   # si appelée au clavier,
            self.after_cancel(self.after_id)    # on évite de lancer la boucle deux fois
        # on programme la prochaine étape, en enregistrant l'id
        # l'id permet d'annuler la prochaine étape avec after_cancel
        self.after_id = self.after(self.periodeDeplacement, self.mouvementBas)

    def mouvementGauche(self, evenement=None):
        """Déplace la pièce d'un rang vers la gauche"""

        if self.enPause:
            return

        obstacle = False
        for brique in self.piece.briques:                                                               # on vérifie si un obstacle est rencontré
            if self.abscissePiece + brique["abscisse"] <= 0 or self.grille[self.abscissePiece+brique["abscisse"]-1][self.ordonneePiece+brique["ordonnee"]] != None:
                obstacle = True
                break

        if not obstacle:                # si la place est libre,
            self.abscissePiece -= 1     # on déplace la pièce
            self.dessiner()             # et on redessine

    def mouvementDroite(self, evenement=None):
        """Déplace la pièce d'un rang vers la droite"""

        if self.enPause:
            return

        obstacle = False
        for brique in self.piece.briques:                                                               # on vérifie si un obstacle est rencontré
            if self.abscissePiece + brique["abscisse"] >= self.nbColonnes-1 or self.grille[self.abscissePiece+brique["abscisse"]+1][self.ordonneePiece+brique["ordonnee"]] != None:
                obstacle = True
                break

        if not obstacle:                # si la place est libre,
            self.abscissePiece += 1     # on déplace la pièce
            self.dessiner()             # et on redessine

    def retournerPiece(self, evenement=None):
        """Tourne la pièce de 90° vers la droite"""

        if self.enPause:
            return

        pieceRetournee = self.piece.retourner()

        # on modifie les coordonnées de la nouvelle pièce
        ordonneePieceTest = self.ordonneePiece + int(self.piece.hauteur/2 - pieceRetournee.hauteur/2)
        # on teste différentes abscisses
        for decalage in [0, -1, 1, -2, 2]:
            abscissePieceTest = self.abscissePiece + int(self.piece.largeur/2 - pieceRetournee.largeur/2) + decalage
            obstacle = False
            for brique in pieceRetournee.briques:   # on vérifie si un obstacle est rencontré
                if abscissePieceTest + brique["abscisse"] < 0 or abscissePieceTest + brique["abscisse"] >= self.nbColonnes or self.grille[abscissePieceTest+brique["abscisse"]][ordonneePieceTest+brique["ordonnee"]] != None:
                    obstacle = True
                    break
            if not obstacle:
                self.piece = pieceRetournee
                self.abscissePiece, self.ordonneePiece = abscissePieceTest, ordonneePieceTest
                self.dessiner()
                break

    def nouvellePartie(self, difficulte, limiterScore):
        """Prépare une nouvelle partie, à appeler avant de lancer"""

        # création du tableau 2D qui représente la grille :
        # pour chaque colonne, on crée une case vide par ligne (voir le compte rendu)
        self.grille = [[None for i in range(self.nbLignes)] for j in range(self.nbColonnes)]

        self.difficulte = difficulte                    # quand la difficulté augmente,
        self.periodeDeplacement = 1000//difficulte      # la vitesse augmente...

        if limiterScore:
            self.scoreMaximal = 11000-1000*difficulte   # ...et le score à atteindre baisse
        else:
            self.scoreMaximal = None
        self.limiterScore = limiterScore

        self.score = 0          # compteur de score
        self.enPause = True     # indique si l'animation est en cours
        self.piece = None       # contient la pièce actuellement en mouvement

        # on calcule la taille des lignes et des colonnes en pixels
        self.largeurColonne = self.winfo_width()/self.nbColonnes
        self.hauteurLigne = self.winfo_height()/self.nbLignes

        # on initialise l'affichage du score
        self.rappelScoreChange(self.score, self.limiterScore, self.scoreMaximal)

        self.dessiner()

        self.prochainePiece = _PieceMelobrics()

        self.rappelNouvellePartie()

    def changerPause(self, enPause=None):
        """Lance le jeu ou le met en pause.
           Si enPause n'est pas fourni, on inverse."""

        if (enPause == None and self.enPause) or enPause == False:
            self.enPause = False                # On lance le jeu.
            self.mouvementBas()
        elif (enPause == None and not self.enPause) or enPause == True:
            self.enPause = True                 # On arrête le jeu,
            try:
                self.after_cancel(self.after_id)    # et on déprogramme la prochaine étape (par sécurité).
            except AttributeError:
                pass

        self.rappelPause(self.enPause)

    def partieTerminee(self, gagne):
        """Termine la partie et efface le dessin"""

        self.changerPause(True)             # On arrête le jeu,
        self.rappelPartieTerminee(self.score, self.difficulte, gagne)    # on informe le joueur,
        self.delete(ALL)                    # on efface la grille,
        self.rappelNouvellePiece(None)      # et on efface la prochaine pièce affichée.

    def dessiner(self):
        """Dessine la grille"""

        # on efface l'ancien dessin
        self.delete(ALL)

        # on dessine une grille vide
        for verticale in range(self.nbColonnes):
            self.create_line(verticale*self.largeurColonne, 0, verticale*self.largeurColonne, self.winfo_height(), fill="grey")
        for horizontale in range(self.nbLignes):
            self.create_line(0, horizontale*self.hauteurLigne, self.winfo_width(), horizontale*self.hauteurLigne, fill="grey")

        # on dessine chaque case pleine de la grille
        for colonne in range(self.nbColonnes):              # pour chaque
            for ligne in range(self.nbLignes):              # case de la grille,
                if self.grille[colonne][ligne] != None:     # si la case est pleine,
                    self.create_rectangle(                  # on dessine un rectangle
                        colonne*self.largeurColonne,                    # abscisse supérieure gauche
                        ligne*self.hauteurLigne,                        # ordonnée supérieure gauche
                        (colonne+1)*self.largeurColonne,                # abscisse inférieure droite
                        (ligne+1)*self.hauteurLigne,                    # ordonnée inférieure droite
                        fill=self.grille[colonne][ligne]["couleur"]     # couleur du rectangle
                    )

        # puis on dessine la pièce en déplacement
        if self.piece != None:
            for brique in self.piece.briques:   # pour chaque brique de la pièce,
                self.create_rectangle(          # on dessine un rectangle
                    (self.abscissePiece+brique["abscisse"])*self.largeurColonne,    # abscisse supérieure gauche
                    (self.ordonneePiece+brique["ordonnee"])*self.hauteurLigne,      # ordonnée supérieure gauche
                    (self.abscissePiece+brique["abscisse"]+1)*self.largeurColonne,  # abscisse inférieure droite
                    (self.ordonneePiece+brique["ordonnee"]+1)*self.hauteurLigne,    # ordonnée inférieure droite
                    fill=self.piece.couleur                                         # couleur du rectangle = couleur de la pièce
                )

    def destroy(self):
        """Déprogramme la prochaine étape avant de détruire le widget.
           Evite un message d'erreur en quittant le jeu sans pause et en laissant Python ouvert
           (l'étape restait programmée même après la fin du programme)."""

        try:
            self.after_cancel(self.after_id)    # on annule la prochaine étape
        except AttributeError:                  # s'il n'y avait pas de prochaine étape,
            pass                                # ça ne change rien
        super().destroy()                       # on détruit le widget


class CanvasPiece(Canvas):
    """Widget permettant d'afficher une seule pièce.
       Sert à afficher la prochaine pièce pendant une partie."""

    def __init__(self, maitre, largeur, hauteur):
        """Initialise le widget"""

        # on appelle le constructeur de Canvas
        super().__init__(maitre, width=largeur, height=hauteur)

        # on ajoute une bordure
        self.config(highlightbackground="black")

        # on calcule la largeur et la longueur maximales d'une pièce
        self.nbColonnes, self.nbLignes = 0, 0
        for piece in _FORMES_PIECES:            # pour chaque pièce disponible,
            for brique in piece:                # on calcule les coordonnées maximale d'une brique
                self.nbColonnes = max(self.nbColonnes, brique["abscisse"]+1)
                self.nbLignes = max(self.nbLignes, brique["ordonnee"]+1)

        # on enregistre la taille du widget
        self.largeur, self.hauteur = largeur, hauteur

        # on calcule la taille en pixels des lignes et colonnes,
        # en se basant sur la taille maximale d'une pièce
        self.largeurColonne = (self.largeur-2) // self.nbColonnes
        self.hauteurLigne = (self.hauteur-2) // self.nbLignes

    def changerPiece(self, piece):
        """Change la pièce affichée"""

        self.piece = piece

        if self.piece != None:  # s'il y  une pièce à afficher
            # on calcule la position du dessin
            # (à quel endroit on devra le dessiner pour qu'il soit au milieu)
            self.largeurDessin = self.largeurColonne*self.piece.largeur
            self.hauteurDessin = self.hauteurLigne*self.piece.hauteur
            self.abscisseDessin = int((self.largeur-self.largeurDessin)/2) + 2
            self.ordonneeDessin = int((self.hauteur-self.hauteurDessin)/2) + 2

        # on dessine la nouvelle pièce
        self.dessiner()

    def dessiner(self):
        """Dessine la pièce"""

        self.delete(ALL)    # on efface le dessin précédent

        if self.piece != None:  # s'il y a une pièce à afficher,
                                # on dessine chaque brique de la pièce
            for brique in self.piece.briques:       # pour chaque brique de la pièce,
                self.create_rectangle(              # on dessine un rectangle
                    self.abscisseDessin+brique["abscisse"]*self.largeurColonne,     # abscisse supérieure gauche
                    self.ordonneeDessin+brique["ordonnee"]*self.hauteurLigne,       # ordonnée supérieure gauche
                    self.abscisseDessin+(brique["abscisse"]+1)*self.largeurColonne, # abscisse inférieure droite
                    self.ordonneeDessin+(brique["ordonnee"]+1)*self.hauteurLigne,   # ordonnée inférieure droite
                    fill=self.piece.couleur                                         # couleur du rectangle = couleur de la pièce
                )

