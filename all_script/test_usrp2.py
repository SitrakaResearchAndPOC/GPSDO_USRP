#!/usr/bin/env python3
from uhd import usrp
import time

# Crée l'objet USRP (USB par défaut)
usrp_device = usrp.MultiUSRP("")

# Force l'utilisation de l'horloge externe
usrp_device.set_clock_source("gpsdo")
time.sleep(0.1)  # petit délai pour que le changement prenne effet

# Lis la fréquence réelle du master clock
mc_rate = usrp_device.get_master_clock_rate()

# Horloge attendue pour B210 avec source externe (souvent 16 MHz)
expected_mc_rate = 16e6  # Hz

print(f"(master clock = {mc_rate/1e6:.6f} MHz)")


# Vérifie ref_locked
ref_locked = usrp_device.get_mboard_sensor("ref_locked", 0).value
print(f"ref_locked (indicateur UHD) = {ref_locked}")

# Affiche tous les capteurs disponibles sur la carte mère 0
sensor_names = usrp_device.get_mboard_sensor_names(0)
print("Capteurs disponibles :", sensor_names)

# Vérifie si ref_locked est présent et affiche sa valeur
if "ref_locked" in sensor_names:
    ref_sensor = usrp_device.get_mboard_sensor("ref_locked", 0)
    print("ref_locked :", ref_sensor.value)
else:
    print("Capteur 'ref_locked' non trouvé sur la carte mère 0")
