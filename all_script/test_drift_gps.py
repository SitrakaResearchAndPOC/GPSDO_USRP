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
import matplotlib.pyplot as plt
import numpy as np

usrp = usrp.MultiUSRP("")

usrp.set_clock_source("gpsdo")
usrp.set_time_source("gpsdo")
time.sleep(2)

t_data = []
err_data = []

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1)

ax.set_title("REAL GPSDO noise (no artifacts)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("PPS phase error (ns)")
ax.grid(True)

start = time.time()

print("Measuring real PPS phase noise...")

while True:

    # 🔥 vraie base physique : temps USRP au PPS
    try:
        usrp_t = usrp.get_time_last_pps().get_real_secs()
    except:
        usrp_t = usrp.get_time_now().get_real_secs()

    # 🔥 GPS time (référence absolue)
    gps_t = float(usrp.get_mboard_sensor("gps_time", 0).value)

    # ⚠️ on compare uniquement la partie fractionnaire PPS
    error = (usrp_t - int(usrp_t)) - (gps_t - int(gps_t))

    t = time.time() - start

    t_data.append(t)
    err_data.append(error * 1e9)  # ns

    line.set_xdata(np.array(t_data))
    line.set_ydata(np.array(err_data))

    ax.relim()
    ax.autoscale_view()

    plt.pause(0.05)
