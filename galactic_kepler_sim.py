import pygame
import math
import random

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
        
        # 1. DISQUE D'ACCRÉTION (5%) - Le coeur chaud
        if aleatoire < 0.05:
            self.distance = random.uniform(RAYON_TROU_NOIR + 5, 80)
            self.angle = random.uniform(0, 2*math.pi)
            
            # Dégradé thermique : bleu/blanc près du centre
            chaleur = 1 - ((self.distance - RAYON_TROU_NOIR) / 80)
            r = 255
            g = int(100 + 155 * chaleur)
            b = int(50 + 205 * chaleur)
            self.couleur = (r, g, b)
            self.taille = random.uniform(1.0, 2.5)
            self.epaisseur = 2 

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
            
            # Couleur orangée (Vieilles étoiles géantes rouges)
            v = random.randint(0, 50)
            self.couleur = (255, 200 + v, 100 + v)
            self.taille = random.uniform(1.2, 2.2)
            self.epaisseur = 15

        # 3. BRAS SPIRAUX (80%)
        else:
            # Liste des bras majeurs de la Voie Lactée
            BRAS = [
                {"nom": "Ecu-Croix", "angle": 0.0, "coul": (50, 150, 255)}, 
                {"nom": "Persee", "angle": 2.2, "coul": (30, 100, 255)},
                {"nom": "Sagittaire", "angle": 3.8, "coul": (100, 180, 255)},
                {"nom": "Regle", "angle": 5.2, "coul": (80, 120, 200)}
            ]
            
            # Petit bras d'Orion (où nous sommes)
            if random.random() < 0.1:
                bras = {"nom": "Orion", "angle": 1.1, "coul": (200, 200, 255)}
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
            
            c_base = bras["coul"]
            self.couleur = (
                min(255, max(0, c_base[0] + random.randint(-40, 40))),
                min(255, max(0, c_base[1] + random.randint(-40, 40))),
                min(255, max(0, c_base[2] + random.randint(-40, 40)))
            )
            self.taille = random.uniform(0.5, 1.8)
            self.epaisseur = 10 + (250 / (self.distance/10 + 1))

        # Position verticale aléatoire (épaisseur du disque)
        self.y_offset = random.gauss(0, self.epaisseur/1.5)


    def dessiner(self, surface, centre_x, centre_y, temps, mat_x, mat_y, afficher_texte):
        if not self.est_galaxie:
            # Scintillement du fond (effet de respiration)
            # On utilise sin() pour faire varier la luminosité
            pulse = math.sin(temps * 2.0 + self.phase_clignotement) 
            facteur = 0.5 + 0.5 * pulse 
            val = int(100 + 155 * facteur) 
            coul_fond = (val, val, val)
            pygame.draw.circle(surface, coul_fond, (int(self.x), int(self.y)), 1)
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
                    txt = font.render(f"Système Solaire (Vous)", True, (255, 255, 150))
                    surface.blit(txt, (ecran_x + 20, ecran_y - 20))
            else:
                # ETOILE NORMALE
                taille = max(1, int(self.taille * scale))
                if taille == 1:
                    surface.set_at((int(ecran_x), int(ecran_y)), couleur_finale)
                else:
                    s = pygame.Surface((taille*2, taille*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*couleur_finale, 180), (taille, taille), taille)
                    surface.blit(s, (ecran_x-taille, ecran_y-taille))

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
        
        for etoile in etoiles_galaxie:
            if etoile.est_vagabonde:
                # Les vagabondes ont déjà leurs coords 3D calculées dans dessiner()
                # Mais ici on doit anticiper leur position pour le tri Z...
                # Pour simplifier, on prend leurs coords actuelles stockées
                # (Léger décalage d'une frame, invisible à l'oeil)
                x, y, z = etoile.x_3d, etoile.y_3d, etoile.z_3d
            else:
                # Simulation position orbitale (Kepler)
                r = max(10, etoile.distance)
                v = math.sqrt(MASSE_TROU_NOIR / r) * 1.5
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

        # 3. Interface Utilisateur (Légende)
        if afficher_legendes:
            legende = [
                ("Trou Noir Supermassif (Sagittarius A*)", (0, 0, 0)),
                ("Barre Galactique (Vieilles Etoiles)", (255, 200, 100)),
                ("Bras Spiraux (Formation Stellaire)", (50, 150, 255)),
                ("Système Solaire (Vous)", (255, 255, 0))
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