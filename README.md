# Sagittarius-A-Engine

**Calculateur de dynamique stellaire et rendu 3D haute performance pour Sagittarius A*.**

Ce projet est un moteur de simulation astrophysique développé "from scratch" en Python. Il modélise la structure de la Voie Lactée et les interactions gravitationnelles complexes autour de son trou noir supermassif central.

---

##  Fondations Mathématiques & Algorithmiques

L'objectif principal de ce moteur est de démontrer une implémentation manuelle de concepts mathématiques avancés sans recourir à des bibliothèques de calcul tierces.

### 1. Algèbre Linéaire & Transformations 3D
* **Matrices de Rotation** : Utilisation de matrices de passage pour les rotations $R_x(\theta)$ et $R_y(\theta)$ afin de manipuler l'inclinaison galactique.
* **Produit Matriciel** : Implémentation du produit ligne par colonne dans une classe `Matrice3x3` personnalisée pour transformer les vecteurs de position.
* **Projection Perspective** : Conversion des coordonnées spatiales $(x, y, z)$ vers le plan de l'écran avec un facteur d'échelle dynamique.



### 2. Dynamique Stellaire & Physique
* **Modélisation de Kepler** : Simulation de la vitesse orbitale basée sur la distance radiale $v = \sqrt{\frac{GM}{r}}$, respectant les lois de la mécanique céleste.
* **Géométrie Procédurale** : Génération des bras via des **spirales logarithmiques** ($r = a e^{b\theta}$) et utilisation de **distributions gaussiennes** pour l'épaisseur du disque.
* **Lentille Gravitationnelle** : Calcul en temps réel de la déviation lumineuse (rayon d'Einstein) pour les objets passant derrière la singularité centrale.

---

## 🚀 Installation et Lancement

1. **Prérequis** : Assurez-vous d'avoir Python installé et la bibliothèque **Pygame**.
   ```bash
   pip install pygame


2. **Lancement :**
    ```bash
    python sagittarius_engine.py

---

## 🎮 Commandes Interactives
* **Souris (Clic gauche + Glisser)** : Rotation de la caméra sur les axes X et Y.
* **Espace** : Régénération procédurale de la galaxie.
* **L** : Affichage des légendes techniques et de la télémétrie.

---

## 📂 Structure du Code
* **Matrice3x3** : Moteur de calcul algébrique personnalisé pour les transformations linéaires (Rotation X, Y et produit matriciel).
* **Etoile** : Classe gérant les états physiques (position 3D, vitesse orbitale, couleur thermique et cycle de vie).
* **dessiner_trou_noir** : Algorithme de rendu visuel pour l'horizon des événements et le halo photonique de Sagittarius A*.

  
<p align="center">
  <img src="https://github.com/user-attachments/assets/bf4cf025-d1e6-484b-b4bc-168ccf4476de" width="800" alt="voie_lactée">
</p>
  
