import pygame
import math
import random
import os

# --- Configuration de la fenêtre ---
LARGEUR, HAUTEUR = 1200, 800
FPS = 60
NB_ETOILES_GALAXIE = 5000
NB_ETOILES_FOND = 200

# --- Paramètres Physiques (Inspiré de Newton/Kepler) ---
MASSE_TROU_NOIR = 2500       
RAYON_TROU_NOIR = 15       
FORCE_LENTILLE = 3500  

# --- Couleurs ---
COULEUR_ESPACE = (5, 5, 10)

def couleur_corps_noir(temp):
    """
    Fonction mathématique qui approxime la couleur d'une étoile selon sa température (Loi de Planck/Wien).
    C'est de l'analyse : Température (K) -> Couleur (RGB).
    """
    # Bornes pour éviter les erreurs de calcul
    temp = max(1000, min(temp, 40000))
    
    if temp < 3500: 
        # Étoiles froides (Naines Rouges, Géantes Rouges) - 3000K
        r = 255
        g = min(255, int(temp / 3500 * 150)) 
        b = min(255, int(temp / 3500 * 50))
    elif temp < 6000:
        # Étoiles type Soleil (Jaune/Blanc) - 5000K-6000K
        # Interpolation linéaire (Fonction affine y = ax + b)
        t = (temp - 3500) / 2500 # t va de 0 à 1
        r = 255
        g = int(150 + 105 * t) # Vert augmente
        b = int(50 + 205 * t)  # Bleu augmente
    else:
        # Étoiles chaudes (Bleues) - >10000K
        # Ici le rouge diminue car le spectre glisse vers l'UV
        t = (temp - 6000) / 34000
        r = int(255 - 150 * t)
        g = int(255 - 50 * t)
        b = 255
        
    return (r, g, b)

# --- CLASSES DU COURS DE MATHS (Code personnel) ---
class Matrice3x3:
    """
    Classe faite maison pour gérer les transformations linéaires (Rotation).
    On n'utilise pas numpy pour bien montrer qu'on a compris le chapitre sur les matrices.
    """
    def __init__(self, lignes=None):
        if lignes:
            self.valeurs = lignes
        else:
            # Matrice Identité (Diagonale de 1, le reste à 0)
            self.valeurs = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    @staticmethod
    def rotation_y(angle):
        """ Matrice de rotation autour de l'axe Y (Vertical) """
        c = math.cos(angle)
        s = math.sin(angle)
        # Formule du cours pour la rotation Y :
        # [ cos(a)  0  sin(a) ]
        # [   0     1    0    ]
        # [-sin(a)  0  cos(a) ]
        return Matrice3x3([
            [c,  0, s],
            [0,  1, 0],
            [-s, 0, c]
        ])

    @staticmethod
    def rotation_x(angle):
        """ Matrice de rotation autour de l'axe X (Horizontal) """
        c = math.cos(angle)
        s = math.sin(angle)
        # Formule du cours pour la rotation X :
        # [ 1    0      0   ]
        # [ 0  cos(a) -sin(a)]
        # [ 0  sin(a)  cos(a)]
        return Matrice3x3([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c]
        ])

    def multiplier_vecteur(self, x, y, z):
        """ 
        Applique la transformation M * V.
        C'est un produit matriciel ligne par colonne.
        """
        v = self.valeurs
        # x' = l1.x + l1.y + l1.z ...
        nx = v[0][0]*x + v[0][1]*y + v[0][2]*z
        ny = v[1][0]*x + v[1][1]*y + v[1][2]*z
        nz = v[2][0]*x + v[2][1]*y + v[2][2]*z
        return nx, ny, nz

class GalaxieVoisine:
    def __init__(self, nom, x, y, z, couleur, taille_base, type_g="spirale", image_nom=None):
        self.nom = nom
        self.x = x
        self.y = y
        self.z = z
        self.couleur = couleur
        self.taille_base = taille_base
        self.type_g = type_g # "spirale" ou "nuage"
        self.image = None
        
        # Tentative de chargement de la vraie photo
        if image_nom:
            try:
                chemin = os.path.join(os.path.dirname(__file__), image_nom)
                if os.path.exists(chemin):
                    # .convert_alpha() est important pour la transparence d'un PNG
                    self.image = pygame.image.load(chemin).convert_alpha()
                    print(f"Image chargée avec succès : {image_nom}")
            except Exception as e:
                print(f"Erreur chargement image {image_nom}: {e}")

    def dessiner(self, surface, cx, cy, scale):
        # Taille apparente
        taille = int(self.taille_base * scale)
        if taille < 2: taille = 2
        
        # Position écran
        px, py = int(cx), int(cy)

        # SI UNE IMAGE EXISTE -> AFFICHER LA PHOTO
        if self.image:
            # On calcule une taille d'affichage basée sur la distance
            taille_img = int(taille * 8) # Facteur de grossissement
            
            # --- SECURITE ANTI-CRASH ---
            # Si la galaxie passe trop près de la caméra, la taille explose (ex: 15000 pixels).
            # Pygame essaie d'allouer 1 Go de RAM pour l'image et plante.
            # On plafonne la taille à 600 pixels max.
            taille_img = min(taille_img, 600)
            
            if taille_img > 5:
                # Redimensionnement propre
                try:
                    img_scaled = pygame.transform.smoothscale(self.image, (taille_img, taille_img))
                    # Centrer l'image sur px, py
                    rect = img_scaled.get_rect(center=(px, py))
                    surface.blit(img_scaled, rect)
                except Exception as e:
                    # En cas d'erreur mémoire, on ignore juste ce dessin pour cette frame
                    pass
        
        # SINON -> DESSIN PROCÉDURAL (Code de secours)
        elif self.type_g == "spirale":
            # Dessin simplifié d'Andromède (disque incliné)
            rect = pygame.Rect(0, 0, taille*4, taille*2)
            rect.center = (px, py)
            pygame.draw.ellipse(surface, (*self.couleur, 100), rect)
            pygame.draw.ellipse(surface, (255, 255, 255, 150), rect, width=2)
            # Petit noyau
            pygame.draw.circle(surface, (255, 240, 200), (px, py), taille//2)
            
        else:
            # Dessin des nuages de Magellan (taches irrégulières)
            for _ in range(10):
                ox = random.randint(-taille, taille)
                oy = random.randint(-taille, taille)
                pygame.draw.circle(surface, (*self.couleur, 50), (px+ox, py+oy), taille//3)

        # Nom
        font = pygame.font.SysFont("Arial", 10)
        txt = font.render(self.nom, True, (150, 150, 150))
        surface.blit(txt, (px + taille//2, py + taille))


class Etoile:
    def __init__(self, est_galaxie=True, est_vagabonde=False):
        self.est_galaxie = est_galaxie
        self.est_vagabonde = est_vagabonde
        self.est_soleil = False 
        # Décalage pour le scintillement (chaque étoile brille à son rythme)
        self.phase_clignotement = random.uniform(0, 2 * math.pi)
        self.initialiser()
        
    def initialiser(self):
        if not self.est_galaxie:
            # Étoiles du fond (décor) - coordonnées écran directes
            self.x = random.randint(0, LARGEUR)
            self.y = random.randint(0, HAUTEUR)
            # Clignotement
            self.couleur_base = random.randint(150, 255)
            # Pas de coordonnées 3D pour le fond simple
            return

        # 0. ETOILES VAGABONDES (Hypervéloces) - Hors de la galaxie
        if self.est_vagabonde:
            # Départ aléatoire proche du centre (éjection)
            self.x_3d = random.uniform(-50, 50)
            self.y_3d = random.uniform(-20, 20)
            self.z_3d = random.uniform(-50, 50)
            
            # Vecteur Vitesse (Très rapide, s'éloigne du centre)
            # On utilise les vecteurs aléatoires normalisés
            vx = random.uniform(-1, 1)
            vy = random.uniform(-0.5, 0.5) 
            vz = random.uniform(-1, 1)
            norme = math.sqrt(vx**2 + vy**2 + vz**2)
            
            vitesse = random.uniform(1.5, 2.5) # Vitesse constante "Lineaire"
            self.vx = (vx / norme) * vitesse
            self.vy = (vy / norme) * vitesse
            self.vz = (vz / norme) * vitesse
            
            self.couleur = (200, 200, 255) # Bleu très chaud
            self.taille = random.uniform(1.0, 1.5)
            return

        # --- GÉNÉRATION DE LA GALAXIE (MODELE PERSO) ---
        aleatoire = random.random()
        
        # 1. BULBE GALACTIQUE & DISQUE D'ACCRÉTION (5%)
        # Correction Réaliste : Le centre (Bulbe) est une boule jaune (vieilles étoiles)
        # Seul l'anneau autour du trou noir reste bleu.
        if aleatoire < 0.05:
            self.distance = random.uniform(RAYON_TROU_NOIR + 3, 90)
            self.angle = random.uniform(0, 2*math.pi)
            
            # Zone A : Proche du Trou Noir (Disque d'accrétion violent -> Bleu/UV)
            if self.distance < RAYON_TROU_NOIR + 12:
                self.temp = random.uniform(20000, 50000)
                self.epaisseur = 3 # Le disque est plat
                self.taille = random.uniform(1.5, 3.0)
            
            # Zone B : Le Bulbe Galactique (Population II -> Jaune/Orange)
            else:
                self.temp = random.uniform(3000, 5500) # Soleil ou plus froid
                # Le bulbe est sphérique, donc très épais verticalement par rapport au disque
                self.epaisseur = 60 * (1 - (self.distance/100)) 
                self.taille = random.uniform(1.8, 3.5) # Très lumineux par densité

            self.couleur = couleur_corps_noir(self.temp) 

        # 2. BARRE CENTRALE (15%) - Structure rectangulaire d'étoiles vieilles
        elif aleatoire < 0.20:
            demi_longueur = 140
            largeur = 35
            
            d_long = (random.random() - 0.5) * 2 * demi_longueur
            d_larg = random.gauss(0, largeur)
            
            angle_barre = 0.78 # ~45 degrés
            c = math.cos(angle_barre)
            s = math.sin(angle_barre)
            
            # On place le point dans le rectangle tourné
            x_rot = d_long * c - d_larg * s
            z_rot = d_long * s + d_larg * c
            
            # Conversion en polaire (distance/angle) pour la physique newtonienne plus tard
            self.distance = math.sqrt(x_rot**2 + z_rot**2)
            self.angle = math.atan2(z_rot, x_rot)
            
            # Physique : La barre est composée de VIEILLES étoiles (Froides -> Rouges/Oranges)
            self.temp = random.uniform(2500, 4500)
            self.couleur = couleur_corps_noir(self.temp)
            
            self.taille = random.uniform(1.2, 2.2)
            self.epaisseur = 15

        # 3. BRAS SPIRAUX (80%)
        else:
            # Liste des bras majeurs de la Voie Lactée
            BRAS = [
                {"nom": "Ecu-Croix", "angle": 0.0, "coul": None}, 
                {"nom": "Persee", "angle": 2.2, "coul": None},
                {"nom": "Sagittaire", "angle": 3.8, "coul": None},
                {"nom": "Regle", "angle": 5.2, "coul": None}
            ]
            
            # Petit bras d'Orion (où nous sommes)
            if random.random() < 0.1:
                bras = {"nom": "Orion", "angle": 1.1, "coul": None}
            else:
                bras = random.choice(BRAS)
            
            dist = random.normalvariate(300, 100) + 50 
            if dist > 600: dist = 600
            if dist < 120: dist = 120
           
            # Formule de la spirale logarithmique
            torsion = 0.015 
            angle_final = bras["angle"] + dist * torsion + random.gauss(0, 0.2)
            
            self.distance = dist
            self.angle = angle_final
            
            # Physique : Dans les bras, on trouve les jeunes étoiles (Bleues/Chaudes)
            # Mais aussi beaucoup d'étoiles moyennes. 
            if random.random() < 0.2:
                # 20% d'étoiles massives/jeunes (Bleu brillant)
                self.temp = random.uniform(10000, 30000)
                self.taille = random.uniform(1.5, 2.8)
            else:
                # 80% d'étoiles "normales" (Soleil ou plus froides)
                self.temp = random.uniform(3500, 6500)
                self.taille = random.uniform(0.5, 1.5)
            
            self.couleur = couleur_corps_noir(self.temp)
            self.epaisseur = 10 + (250 / (self.distance/10 + 1))

        # Position verticale aléatoire (épaisseur du disque)
        self.y_offset = random.gauss(0, self.epaisseur/1.5)


    def dessiner(self, surface, centre_x, centre_y, temps, mat_x, mat_y, afficher_texte):
        if not self.est_galaxie:
            # SCINTILLEMENT RÉALISTE (Turbulences atmosphériques)
            # Avant : sin(temps * 2.0) -> Trop lent (respiration)
            # Maintenant : sin(temps * 150.0) -> Rapide (Scintillement ~8Hz)
            
            # Variation rapide
            pulse = math.sin(temps * 150.0 + self.phase_clignotement)
            
            # On ajoute une couche de bruit aléatoire (le chaos de l'air)
            bruit = random.uniform(-0.2, 0.2)
            
            # Intensité finale (entre 0.2 et 1.0)
            intensite = 0.6 + 0.3 * pulse + bruit
            intensite = max(0.1, min(1.0, intensite))
            
            # Conversion en gris (100-255)
            val = int(255 * intensite)
            
            # Parfois (rarement), un petit flash de couleur (chromatisme atmosphérique)
            if intensite > 0.95 and random.random() < 0.1:
                col = (255, 255, 255) # Blanc pur éclatant
            else:
                col = (val, val, val) # Gris variable
                
            pygame.draw.circle(surface, col, (int(self.x), int(self.y)), 1)
            return

        couleur_finale = self.couleur

        # CAS SPÉCIAL : ÉTOILES VAGABONDES (Mouvement Rectiligne Uniforme)
        if self.est_vagabonde:
            # P(t+1) = P(t) + V => Translation
            self.x_3d += self.vx
            self.y_3d += self.vy
            self.z_3d += self.vz
            
            # Reset si trop loin (pour garder l'animation active)
            if math.sqrt(self.x_3d**2 + self.y_3d**2 + self.z_3d**2) > 800:
                self.initialiser()
                
            # Les coordonnées sont déjà calculées
            x, y, z = self.x_3d, self.y_3d, self.z_3d
            
        else:
            # 1. LOIS DE KEPLER SIMULÉES
            # Plus on est proche du centre, plus on tourne vite (Conservation moment cinétique)
            # v = racine(GM / r)
            rayon_eff = max(10, self.distance) 
            vitesse_orbitale = math.sqrt(MASSE_TROU_NOIR / rayon_eff) * 1.5
            
            # Vitesse angulaire w = v / r
            w = vitesse_orbitale / rayon_eff
            angle_courant = self.angle + temps * w * 5.0
            
            # Coordonnées 3D de l'étoile
            x = math.cos(angle_courant) * self.distance
            z = math.sin(angle_courant) * self.distance
            y = self.y_offset
        
        # 2. APPLICATION DES MATRICES POUR LA CAMÉRA
        # Rotation X (Inclinaison de la galaxie)
        rx, ry, rz = mat_x.multiplier_vecteur(x, y, z)
        # Rotation Y (Rotation de la vue)
        fx, fy, final_z = mat_y.multiplier_vecteur(rx, ry, rz)
        
        # 3. PROJECTION (3D -> Écran 2D)
        camera_z = 600
        if camera_z + final_z <= 0: return # Derrière la caméra

        scale = 500 / (camera_z + final_z)
        ecran_x = centre_x + fx * scale
        ecran_y = centre_y + fy * scale # Effet aplati du disque

        # --- BONUS : LENTILLE GRAVITATIONNELLE ---
        # Si une étoile passe derrière le trou noir, la gravité dévie sa lumière
        pos_trou_noir_x, pos_trou_noir_y = centre_x, centre_y 
        
        if final_z > 0: # L'étoile est derrière le plan
            dx = ecran_x - pos_trou_noir_x
            dy = ecran_y - pos_trou_noir_y
            dist_trou_noir = math.sqrt(dx*dx + dy*dy)
            
            rayon_einstein = math.sqrt(FORCE_LENTILLE) * (scale / 5.0)
            
            # Si on est proche du rayon d'Einstein, on déforme
            if dist_trou_noir < rayon_einstein * 4 and dist_trou_noir > 1:
                deformation = (rayon_einstein**2) / dist_trou_noir
                facteur = (dist_trou_noir + deformation) / dist_trou_noir
                
                ecran_x = pos_trou_noir_x + dx * facteur
                ecran_y = pos_trou_noir_y + dy * facteur


        if 0 <= ecran_x < LARGEUR and 0 <= ecran_y < HAUTEUR:
            if self.est_soleil:
                # DESSIN DU SOLEIL (Marqueur Spécial)
                taille = max(3, int(self.taille * scale))
                
                # Halo jaune
                s = pygame.Surface((taille*4, taille*4), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 100, 50), (taille*2, taille*2), taille*2)
                pygame.draw.circle(s, (255, 255, 255, 200), (taille*2, taille*2), taille)
                surface.blit(s, (ecran_x-taille*2, ecran_y-taille*2))
                
                if afficher_texte:
                    pygame.draw.circle(surface, (255, 50, 50), (int(ecran_x), int(ecran_y)), taille+5, 1)
                    font = pygame.font.SysFont("Arial", 12)
                    txt = font.render(f"Système Solaire", True, (255, 255, 150))
                    surface.blit(txt, (ecran_x + 20, ecran_y - 20))
            else:
                # DESSIN CLASSIQUE OPTIMISÉ (Direct sur l'écran)
                # On arrête de créer des surfaces (s = Surface...) car ça sature la mémoire RAM
                taille = max(1, int(self.taille * scale))
                if taille == 1:
                    surface.set_at((int(ecran_x), int(ecran_y)), couleur_finale)
                else:
                    # Dessin direct (beaucoup plus rapide et stable)
                    pygame.draw.circle(surface, couleur_finale, (int(ecran_x), int(ecran_y)), taille)

def dessiner_trou_noir(surface, cx, cy, scale):
    """ Dessine le trou noir et son halo """
    rayon_visuel = RAYON_TROU_NOIR * scale
    if rayon_visuel < 1: return

    # Halo Photonique
    taille_halo = int(rayon_visuel * 1.5)
    s = pygame.Surface((taille_halo*2, taille_halo*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 200, 150, 40), (taille_halo, taille_halo), taille_halo)
    pygame.draw.circle(s, (255, 255, 255, 100), (taille_halo, taille_halo), int(rayon_visuel * 1.1))
    surface.blit(s, (cx - taille_halo, cy - taille_halo))

    # Horizon des événements (Noir absolu)
    pygame.draw.circle(surface, (0, 0, 0), (int(cx), int(cy)), int(rayon_visuel))

def main():
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Projet Voie Lactée (Chef d'Oeuvre)")

    # --- GESTION MUSIQUE (TRANSITION NEKFEU -> INTERSTELLAR) ---
    # Événement personnalisé pour savoir quand l'intro est finie
    FIN_INTRO_EVENT = pygame.USEREVENT + 1
    
    chemin_nekfeu = os.path.join(os.path.dirname(__file__), "nekfeu_intro.mp3")
    chemin_interstellar = os.path.join(os.path.dirname(__file__), "interstellar.mp3")
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)
        
        # 1. On essaie de lancer l'intro de Nekfeu en premier
        if os.path.exists(chemin_nekfeu):
            print("Lancement intro Nekfeu...")
            pygame.mixer.music.load(chemin_nekfeu)
            pygame.mixer.music.play(0) # 0 = Jouer une seule fois
            
            # On demande à Pygame d'envoyer un signal quand c'est fini
            pygame.mixer.music.set_endevent(FIN_INTRO_EVENT)
        
        # 2. Sinon, on lance directement Interstellar
        elif os.path.exists(chemin_interstellar):
            print("Pas d'intro trouvée, lancement direct Interstellar...")
            pygame.mixer.music.load(chemin_interstellar)
            # -1 = boucle infinie, 30.0 = commence à la 30ème seconde
            pygame.mixer.music.play(-1, 30.0)
            
    except Exception as e:
        print(f"Erreur audio : {e}")
    
    # Création des étoiles
    etoiles_fond = [Etoile(est_galaxie=False) for _ in range(NB_ETOILES_FOND)]
    etoiles_galaxie = [Etoile(est_galaxie=True) for _ in range(NB_ETOILES_GALAXIE)]
    
    # Ajout des étoiles Vagabondes (Hypervéloces)
    # Ces étoiles ne suivent pas Kepler, elles sortent du système (Mouvement rectiligne)
    etoiles_vagabondes = [Etoile(est_galaxie=True, est_vagabonde=True) for _ in range(30)]
    etoiles_galaxie.extend(etoiles_vagabondes)
    
    # Ajout manuel du Soleil
    le_soleil = Etoile(est_galaxie=True)
    le_soleil.distance = 350
    le_soleil.angle = 1.1 + 350 * 0.015 
    le_soleil.est_soleil = True
    le_soleil.couleur = (255, 255, 0) # Jaune
    le_soleil.taille = 4.0
    le_soleil.y_offset = 0
    etoiles_galaxie.append(le_soleil)
    
    # --- CREATION GALAXIES VOISINES ---
    # Coordonnées (x, y, z) approximatives à l'échelle
    
    # 1. Andromède (M31) - Notre voisine géante (Image Réaliste .webp)
    # Note : Pygame gère le .webp sur les versions récentes
    andromede = GalaxieVoisine("M31 Andromède", -800, 300, 1500, (200, 200, 255), 30, "spirale", "andromede.webp")
    
    # 2. Petit Nuage de Magellan (Procédural - points diffus)
    # On garde le mode classique qui rend souvent mieux pour les galaxies irrégulières qu'une photo mal détourée
    smc = GalaxieVoisine("Petit Nuage", 350, -250, 700, (180, 180, 200), 7, "nuage")
    
    galaxies_voisines = [andromede, smc]


    temps_global = 0
    inclinaison_x = 0.9 # Angle de vue initial
    rotation_y = 0.0
    vitesse_rot = 0.002
    afficher_legendes = True
    
    police = pygame.font.SysFont("Arial", 14)
    horloge = pygame.time.Clock()

    en_cours = True
    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            
            # --- GESTION DE LA TRANSITION MUSICALE ---
            if evenement.type == FIN_INTRO_EVENT:
                print("Intro finie -> Transition vers Interstellar")
                if os.path.exists(chemin_interstellar):
                    pygame.mixer.music.load(chemin_interstellar)
                    # Commence à la 30ème seconde
                    pygame.mixer.music.play(-1, 30.0)
            
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_SPACE:
                    # Reset
                    etoiles_galaxie = [Etoile(est_galaxie=True) for _ in range(NB_ETOILES_GALAXIE)]
                    etoiles_galaxie.append(le_soleil)
                if evenement.key == pygame.K_l:
                    afficher_legendes = not afficher_legendes

        # Gestion Souris (Cliquer-glisser pour bouger la caméra)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_rel()
            rotation_y += mx * 0.005
            inclinaison_x += my * 0.005
        else:
            pygame.mouse.get_rel() # Pour éviter les sauts
            rotation_y += vitesse_rot

        temps_global += 0.005
        
        ecran.fill(COULEUR_ESPACE)

        # 1. Dessin du fond scintillant
        for etoile in etoiles_fond:
            etoile.dessiner(ecran, LARGEUR//2, HAUTEUR//2, temps_global, None, None, False)

        # 2. Préparation du rendu Galaxie + Trou Noir
        liste_rendu = []
        centre_x, centre_y = LARGEUR//2, HAUTEUR//2
        
        # Création des matrices pour cette frame
        matrice_x = Matrice3x3.rotation_x(inclinaison_x)
        matrice_y = Matrice3x3.rotation_y(rotation_y)
        
        # --- AJOUT DES VOISINES DANS LA LISTE DE RENDU ---
        for gal in galaxies_voisines:
             # On applique les matrices comme pour les étoiles
            tx, ty, tz = matrice_x.multiplier_vecteur(gal.x, gal.y, gal.z)
            fx, fy, fz = matrice_y.multiplier_vecteur(tx, ty, tz)
            
            # On veut qu'elles restent loin, donc on peut tricher un peu sur la distance
            # Ou les laisser telles quelles
            liste_rendu.append((fz, "VOISINE", (gal, fx, fy, fz)))


        for etoile in etoiles_galaxie:
            if etoile.est_vagabonde:
                x, y, z = etoile.x_3d, etoile.y_3d, etoile.z_3d
            else:
                # Simulation position orbitale (Kepler)
                r = max(10, etoile.distance)
                
                # Modèle de "COURBE DE ROTATION PLATE" (Matière Noire)
                # Au lieu de V ~ 1/sqrt(r), la vitesse plafonne.
                # v_kepler : Décroissance rapide (Influence Trou Noir)
                # v_halo : Constante (Influence Matière Noire)
                v_kepler = math.sqrt(MASSE_TROU_NOIR / r) * 1.5
                v_halo = 3.0 # Vitesse minimale maintenue par le "halo invisible"
                
                # La vraie vitesse est une composition (somme des influences ou max)
                v = max(v_kepler, v_halo)
                
                w = v / r
                angle = etoile.angle + temps_global * w * 5.0
                
                x = math.cos(angle) * etoile.distance
                z = math.sin(angle) * etoile.distance
                y = etoile.y_offset
            
            # On applique les matrices pour connaître le Z final (profondeur)
            tx, ty, tz = matrice_x.multiplier_vecteur(x, y, z)
            fx, fy, fz = matrice_y.multiplier_vecteur(tx, ty, tz)
            
            liste_rendu.append((fz, "ETOILE", etoile))
            
        liste_rendu.append((0, "TROU_NOIR", None))
        
        # Tri en fonction de Z (Algorithme du Peintre)
        # On dessine du plus loin au plus proche
        liste_rendu.sort(key=lambda x: x[0], reverse=True)
        
        for z_val, type_obj, obj in liste_rendu:
            if type_obj == "ETOILE":
                obj.dessiner(ecran, centre_x, centre_y, temps_global, matrice_x, matrice_y, afficher_legendes)
            elif type_obj == "TROU_NOIR":
                scale_bh = 500 / (600 + 0)
                dessiner_trou_noir(ecran, centre_x, centre_y, scale_bh)
            elif type_obj == "VOISINE":
                # Récupération des données pré-calculées
                galaxie_obj, fx, fy, fz = obj
                
                camera_z = 600
                if camera_z + fz > 0:
                    scale = 500 / (camera_z + fz)
                    ecran_x = centre_x + fx * scale
                    ecran_y = centre_y + fy * scale
                    galaxie_obj.dessiner(ecran, ecran_x, ecran_y, scale)

        # 3. Interface Utilisateur (Légende)
        if afficher_legendes:
            legende = [
                ("Trou Noir Supermassif (Sagittarius A*)", (0, 0, 0)),
                ("Barre Galactique (Vieilles Etoiles)", (255, 200, 100)),
                ("Bras Spiraux (Formation Stellaire)", (50, 150, 255)),
                ("Système Solaire", (255, 255, 0))
            ]
            y_txt = HAUTEUR - 180
            for nom, col in legende:
                if col == (0,0,0): pygame.draw.rect(ecran, (255,255,255), (9, y_txt-1, 17, 17), 1)
                pygame.draw.rect(ecran, col, (10, y_txt, 15, 15))
                txt_surf = police.render(nom, True, (200, 200, 200))
                ecran.blit(txt_surf, (35, y_txt))
                y_txt += 20
            
            ecran.blit(police.render("Lentille Gravitationnelle Active", True, (100, 255, 100)), (LARGEUR-250, HAUTEUR-30))
        
        ecran.blit(police.render("L: Légende | Espace: Reset | Souris: Tourner", True, (150, 150, 150)), (10, 10))
        
        pygame.display.flip()
        horloge.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
