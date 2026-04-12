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
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# INIT USRP
# -----------------------------
usrp = usrp.MultiUSRP("")

usrp.set_clock_source("gpsdo")
usrp.set_time_source("gpsdo")

time.sleep(3)

print("USRP initialized")
print("Clock:", usrp.get_clock_source(0))
print("Time :", usrp.get_time_source(0))

# -----------------------------
# DATA STORAGE
# -----------------------------
t_axis = []
jitter_ns = []

# -----------------------------
# PLOT SETUP
# -----------------------------
plt.ion()
fig, ax = plt.subplots()

line, = ax.plot([], [], lw=1)

ax.set_title("USRP GPSDO PPS jitter (correct measurement)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Phase error (ns)")
ax.grid(True)

start = time.time()

print("Measuring PPS jitter... CTRL+C to stop")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    # Time at last PPS (USRP internal reference)
    t_pps = usrp.get_time_last_pps().get_real_secs()

    # Current USRP time
    t_now = usrp.get_time_now().get_real_secs()

    # -----------------------------
    # PHASE ERROR (correct way)
    # -----------------------------
    # fractional part of second
    frac_pps = t_pps - np.floor(t_pps)
    frac_now = t_now - np.floor(t_now)

    error = frac_now - frac_pps

    # unwrap around zero
    if error > 0.5:
        error -= 1.0
    if error < -0.5:
        error += 1.0

    # convert to ns
    error_ns = error * 1e9

    # -----------------------------
    # STORE
    # -----------------------------
    t_axis.append(time.time() - start)
    jitter_ns.append(error_ns)

    # -----------------------------
    # PLOT
    # -----------------------------
    line.set_xdata(t_axis)
    line.set_ydata(jitter_ns)

    ax.relim()
    ax.autoscale_view()

    plt.pause(0.05)
