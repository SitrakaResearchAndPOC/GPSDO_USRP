#!/usr/bin/env python3
from uhd import usrp
import time

# Crée l'objet USRP (USB par défaut)
usrp_device = usrp.MultiUSRP("")

# Force l'utilisation de l'horloge externe
usrp_device.set_clock_source("external")
time.sleep(0.1)  # petit délai pour que le changement prenne effet

# Lis la fréquence réelle du master clock
mc_rate = usrp_device.get_master_clock_rate()

# Horloge attendue pour B210 avec source externe (souvent 16 MHz)
expected_mc_rate = 16e6  # Hz

# Tolérance pour petites variations
tolerance = 1e-3

if abs(mc_rate - expected_mc_rate) / expected_mc_rate < tolerance:
    print(f"Horloge externe détectée et appliquée ✅ (master clock = {mc_rate/1e6:.6f} MHz)")
else:
    print(f"Horloge externe NON détectée ❌ (master clock = {mc_rate/1e6:.6f} MHz)")

# Optionnel : vérifier aussi ref_locked pour info
ref_locked = usrp_device.get_mboard_sensor("ref_locked", 0).value
print(f"ref_locked (indicateur UHD) = {ref_locked}")



# Affiche les capteurs disponibles sur la carte mère 0
print("Capteurs disponibles :", usrp.get_mboard_sensor_names(0))

# Récupère le capteur ref_locked
if "ref_locked" in usrp.get_mboard_sensor_names(0):
    ref_locked_sensor = usrp.get_mboard_sensor("ref_locked", 0)
    print("ref_locked :", ref_locked_sensor.value)
else:
    print("Capteur 'ref_locked' non trouvé sur la carte mère 0")
