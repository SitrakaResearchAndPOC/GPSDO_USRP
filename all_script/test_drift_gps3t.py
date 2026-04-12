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

usrp = usrp.MultiUSRP("")
usrp.set_clock_source("gpsdo")
usrp.set_time_source("gpsdo")

time.sleep(5)  # IMPORTANT: laisser lock GPSDO

print("\n--- STABLE GPS vs USRP DRIFT ---\n")

# attendre premier PPS stable
print("Waiting PPS stabilization...")
for _ in range(5):
    usrp.get_time_last_pps()
    time.sleep(1)

gps_ref = float(usrp.get_mboard_sensor("gps_time", 0).value)
usrp_ref = usrp.get_time_last_pps().get_real_secs()

print(f"Initial GPS ref : {gps_ref}")
print(f"Initial USRP ref: {usrp_ref}")

while True:

    gps_time = float(usrp.get_mboard_sensor("gps_time", 0).value)
    usrp_time = usrp.get_time_last_pps().get_real_secs()

    gps_rel = gps_time - gps_ref
    usrp_rel = usrp_time - usrp_ref

    drift = usrp_rel - gps_rel

    print("-----------------------------------")
    print(f"GPS   : {gps_rel:.9f} s")
    print(f"USRP  : {usrp_rel:.9f} s")
    print(f"DRIFT : {drift:.12e} s")
    print("-----------------------------------")

    time.sleep(1)
