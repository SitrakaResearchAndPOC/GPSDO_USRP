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
paths_to_remove = [
    "/usr/lib/python3/dist-packages/uhd",
    "/usr/lib/python3/site-packages/uhd",
]

for p in paths_to_remove:
    if p in sys.path:
        sys.path.remove(p)

# --- 2. Ajouter les chemins comme PYTHONPATH ---
new_paths = [
    "/usr/local/lib/python3.12/dist-packages",
    "/usr/local/lib/python3.12/site-packages",
]

for p in new_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

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


# ==========================================================
#                GPSDO DRIFT MEASUREMENT
# ==========================================================

import uhd
from uhd import usrp
import time
import matplotlib.pyplot as plt
import numpy as np

# ---------------- INIT USRP ----------------
usrp = usrp.MultiUSRP("")

usrp.set_clock_source("gpsdo")
usrp.set_time_source("gpsdo")
time.sleep(2)

# ---------------- DATA ----------------
t_data = []
drift_data = []

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1)

ax.set_title("GPSDO Drift (USRP vs GPS)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Drift (µs)")
ax.grid(True)

start = time.time()

print("\n--- Measuring GPSDO drift ---")

# ---------------- LOOP ----------------
while True:

    try:
        gps_time = float(usrp.get_mboard_sensor("gps_time", 0).value)
    except Exception as e:
        print("Erreur GPS:", e)
        continue

    usrp_time = usrp.get_time_now().get_real_secs()

    # 🔥 DRIFT RÉEL
    drift = (usrp_time - gps_time) * 1e-9  # µs

    t = time.time() - start

    t_data.append(t)
    drift_data.append(drift)

    # ---------------- PLOT ----------------
    line.set_xdata(np.array(t_data))
    line.set_ydata(np.array(drift_data))

    ax.relim()
    ax.autoscale_view()

    plt.pause(0.1)
