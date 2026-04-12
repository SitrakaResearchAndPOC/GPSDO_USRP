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

usrp = usrp.MultiUSRP("")

usrp.set_clock_source("gpsdo")
usrp.set_time_source("gpsdo")
time.sleep(2)

# ---------------- PARAMETERS ----------------
N = 10  # samples
taus = []
adev = []

print("Collecting GPSDO phase samples...")

# ---------------- COLLECT PHASE ERROR ----------------
samples = []

for i in range(N):

    gps_time = float(usrp.get_mboard_sensor("gps_time", 0).value)

    try:
        usrp_time = usrp.get_time_last_pps().get_real_secs()
    except:
        usrp_time = usrp.get_time_now().get_real_secs()

    # phase error (ns)
    err = (usrp_time - gps_time) * 1e9
    samples.append(err)

    time.sleep(0.02)

samples = np.array(samples)

# ---------------- ALLAN DEVIATION ----------------
def allan_variance(data, tau):
    n = len(data)
    m = tau
    if 2*m >= n:
        return None

    diffs = []
    for i in range(n - 2*m):
        y1 = np.mean(data[i:i+m])
        y2 = np.mean(data[i+m:i+2*m])
        diffs.append((y2 - y1)**2)

    return 0.5 * np.mean(diffs)

max_tau = 50

for tau in range(1, max_tau):
    avar = allan_variance(samples, tau)
    if avar is not None:
        taus.append(tau)
        adev.append(np.sqrt(avar))

# ---------------- PLOT ----------------
plt.figure()
plt.loglog(taus, adev, marker='o')
plt.grid(True, which="both")
plt.title("GPSDO Allan Deviation (UHD)")
plt.xlabel("Tau (samples)")
plt.ylabel("ADEV (ns)")
plt.show()
