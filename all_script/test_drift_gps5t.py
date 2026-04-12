#!/usr/bin/env python3
import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt

# AVANT COMPILATION UHD ACTIVER API PYTHON, POUR VOIR OPTION
# cmake .. -LAH | grep -i ENABLE_PYTHON
# cmake .. -LAH | grep -i ENABLE_LIBUHD
# cmake ..   -DENABLE_PYTHON=ON  -DENABLE_LIBUHD=ON -DPYTHON_EXECUTABLE=$(which python3)


# POUR TROUVER LE CHEMIN ACTUEL, UTILISE CE SCRIPT :
# EN PYTHON
# import uhd
# print(uhd.__file__)
# EN BASH : 
# rm -rf /usr/lib/python3/dist-packages/uhd
# rm -rf /usr/lib/python3/site-packages/uhd


# --- 1. Supprimer les chemins UHD ---
# 
paths_to_remove = [
    "/usr/lib/python3/dist-packages/uhd",
    "/usr/lib/python3/site-packages/uhd",  # corrigé ici
]

for p in paths_to_remove:
    if p in sys.path:
        sys.path.remove(p)

# --- 2. Ajouter les chemins comme PYTHONPATH ---
# POUR TROUVER LE NOUVEAU CHEMIN (voir aprés ldconfig de compilation uhd pour nouveau chemin ) 
# cmake .. -LAH | grep -i PYTHONPATH
# EN BASH : 
# export PYTHONPATH=/usr/local/lib/python3.12/dist-packages:$PYTHONPATH
# export PYTHONPATH=/usr/local/lib/python3.12/site-packages:$PYTHONPATH

new_paths = [
    "/usr/local/lib/python3.12/dist-packages",
    "/usr/local/lib/python3.12/site-packages",
]

for p in new_paths:
    if p not in sys.path:
        sys.path.insert(0, p)  # priorité haute

# --- 3. Synchroniser avec la variable d'environnement ---
os.environ["PYTHONPATH"] = ":".join(new_paths) + ":" + os.environ.get("PYTHONPATH", "")

# --- 4. Vérification ---
print("=== Vérification des chemins ajoutés ===")
for p in new_paths:
    if p in sys.path:
        print(f"[OK] {p} est présent dans sys.path")
    else:
        print(f"[ERREUR] {p} n'est PAS présent")

print("\n=== sys.path actuel ===")
for p in sys.path:
    print(p)

import uhd
from uhd import usrp

# --- INITIALISATION DE L'USRP ---
usrp_device = usrp.MultiUSRP("")

# Utiliser le GPSDO comme source d'horloge
usrp_device.set_clock_source("gpsdo")
usrp_device.set_time_source("gpsdo")
time.sleep(5)  # Laisser le GPSDO se verrouiller

# Vérification des capteurs disponibles
sensor_names = usrp_device.get_mboard_sensor_names(0)
print("\nCapteurs disponibles :", sensor_names)

# Vérification du verrouillage GPS
if "gps_locked" in sensor_names:
    try:
        gps_sensor = usrp_device.get_mboard_sensor("gps_locked", 0)
        print(f"GPSDO lock sur satellites : {gps_sensor.value}")
    except RuntimeError as e:
        print("GPS non verrouillé (pas de fix pour le moment)")
        print("Détail :", e)
else:
    print("Capteur 'gps_locked' non disponible")

# --- ALIGNEMENT TEMPOREL GPSDO ---
print("\n--- Synchronisation temporelle GPSDO ---")

time.sleep(2)

usrp_device.set_time_now(uhd.types.TimeSpec(0.0))  # Synchroniser l'heure de l'USRP
usrp_device.set_time_next_pps(uhd.types.TimeSpec(0.0))  # Synchroniser le prochain PPS

# --- Mesure de la dérive ---
print("\n--- Mesure de la Dérive ---")

# Variables de stockage pour les données de dérive
t_axis = []
jitter_ns = []

# Configuration de l'affichage graphique en temps réel
plt.ion()
fig, ax = plt.subplots()

line, = ax.plot([], [], lw=1)
ax.set_title("Dérive GPSDO vs USRP (Jitter)")
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Erreur de phase (ns)")
ax.grid(True)

# Référence initiale GPS et USRP
gps_ref = float(usrp_device.get_mboard_sensor("gps_time", 0).value)
usrp_ref = usrp_device.get_time_last_pps().get_real_secs()

print(f"Initial GPS ref : {gps_ref}")
print(f"Initial USRP ref: {usrp_ref}")

# Mesure continue de la dérive
start = time.time()

print("Mesure continue de la dérive (CTRL+C pour arrêter)...")

while True:
    gps_time = float(usrp_device.get_mboard_sensor("gps_time", 0).value)
    usrp_time = usrp_device.get_time_last_pps().get_real_secs()

    # Utilisation de la partie fractionnaire pour calculer la dérive
    gps_frac = gps_time - int(gps_time)
    usrp_frac = usrp_time - int(usrp_time)

    # Calcul de la dérive en utilisant la partie fractionnaire
    drift = usrp_frac - gps_frac

    # Conversion de la dérive en nanosecondes
    drift_ns = drift * 1e9  # Convertir la dérive en ns

    # Stockage des données pour le graphique
    t_axis.append(time.time() - start)
    jitter_ns.append(drift_ns)

    # Mise à jour du graphique en temps réel
    line.set_xdata(np.array(t_axis))
    line.set_ydata(np.array(jitter_ns))

    ax.relim()
    ax.autoscale_view()

    plt.pause(0.05)

    # Affichage des valeurs de dérive
    print("-----------------------------------")
    print(f"GPS   : {gps_frac:.9f} s")
    print(f"USRP  : {usrp_frac:.9f} s")
    print(f"DRIFT : {drift:.12e} s")
    print(f"DRIFT (ns) : {drift_ns:.9f} ns")
    print("-----------------------------------")

    time.sleep(0.1)  # Délai plus court pour une meilleure résolution
