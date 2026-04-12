#!/usr/bin/env python3
from uhd import usrp
import time

usrp_device = usrp.MultiUSRP("")
usrp_device.set_clock_source("gpsdo")

time.sleep(2)

sensor_names = usrp_device.get_mboard_sensor_names(0)
print("Capteurs disponibles :", sensor_names)

# --- REF LOCK (le plus fiable) ---
if "ref_locked" in sensor_names:
    try:
        ref = usrp_device.get_mboard_sensor("ref_locked", 0).value
        print("ref_locked =", ref)
    except Exception as e:
        print("Erreur ref_locked :", e)

# --- GPS SERVO (meilleur indicateur GPS réel) ---
gps_locked = False

if "gps_servo" in sensor_names:
    try:
        servo = usrp_device.get_mboard_sensor("gps_servo", 0).value
        print("gps_servo =", servo)

        if "locked" in servo.lower():
            gps_locked = True
    except Exception as e:
        print("Erreur gps_servo :", e)

print("GPS LOCK (estimé) =", gps_locked)

# --- GPS TIME ---
if "gps_time" in sensor_names:
    try:
        gps_time = usrp_device.get_mboard_sensor("gps_time", 0).value
        print("GPS time =", gps_time)
    except Exception as e:
        print("Erreur gps_time :", e)
