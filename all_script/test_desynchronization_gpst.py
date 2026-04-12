#!/usr/bin/env python3
import sys
import os
import time

# --- PATH SETUP (inchangé) ---
paths_to_remove = [
    "/usr/lib/python3/dist-packages/uhd",
    "/usr/lib/python3/site-packages/uhd",
]

for p in paths_to_remove:
    if p in sys.path:
        sys.path.remove(p)

new_paths = [
    "/usr/local/lib/python3.12/dist-packages",
    "/usr/local/lib/python3.12/site-packages",
]

for p in new_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ["PYTHONPATH"] = ":".join(new_paths)

# ==========================================================
#                RAW VALUE DISPLAY (NO FILTER)
# ==========================================================

import uhd
from uhd import usrp

usrp = usrp.MultiUSRP("")

usrp.set_clock_source("gpsdo")
usrp.set_time_source("gpsdo")
time.sleep(2)

print("\n--- RAW GPS vs USRP VALUES ---\n")

gps_ref = None
usrp_ref = None

while True:

    gps_time = float(usrp.get_mboard_sensor("gps_time", 0).value)
    usrp_time = usrp.get_time_now().get_real_secs()

    # référence initiale (pour éviter gros offset constant)
    if gps_ref is None:
        gps_ref = gps_time
        usrp_ref = usrp_time

    # valeurs relatives
    gps_rel = gps_time - gps_ref
    usrp_rel = usrp_time - usrp_ref

    # soustraction EXACTE
    diff = usrp_rel - gps_rel

    print("\n===================================")
    print(f"GPS time absolute   : {gps_time}")
    print(f"USRP time absolute  : {usrp_time}")
    print("-----------------------------------")
    print(f"GPS relative        : {gps_rel}")
    print(f"USRP relative       : {usrp_rel}")
    print("-----------------------------------")
    print(f"USRP - GPS (drift)  : {diff} seconds")
    print("===================================")

    time.sleep(1)
