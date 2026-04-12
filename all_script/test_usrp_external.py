#!/usr/bin/env python3
import sys
import os
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
import time

# Crée l'objet USRP (USB par défaut)
usrp_device = usrp.MultiUSRP("")

# Force l'utilisation de l'horloge externe
usrp_device.set_clock_source("external")
time.sleep(0.1)

# Lis la fréquence réelle du master clock
mc_rate = usrp_device.get_master_clock_rate()

expected_mc_rate = 16e6  # Hz
tolerance = 1e-3

if abs(mc_rate - expected_mc_rate) / expected_mc_rate < tolerance:
    print(f"Horloge externe détectée et appliquée ✅ (master clock = {mc_rate/1e6:.6f} MHz)")
else:
    print(f"Horloge externe NON détectée ❌ (master clock = {mc_rate/1e6:.6f} MHz)")

# Vérification ref_locked
ref_locked = usrp_device.get_mboard_sensor("ref_locked", 0).value
print(f"ref_locked (indicateur UHD) = {ref_locked}")

# Capteurs disponibles
sensor_names = usrp_device.get_mboard_sensor_names(0)
print("Capteurs disponibles :", sensor_names)

# Vérification ref_locked propre
if "ref_locked" in sensor_names:
    ref_locked_sensor = usrp_device.get_mboard_sensor("ref_locked", 0)
    print("ref_locked :", ref_locked_sensor.value)
else:
    print("Capteur 'ref_locked' non trouvé sur la carte mère 0")
