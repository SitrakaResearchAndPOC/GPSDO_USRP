# OCXO 
# GPDO integrated on USRP

<p align="center">
  <img src="https://github.com/SitrakaResearchAndPOC/OCXO_USRP/blob/main/gpsdo1.png" width="200" />
  <img src="https://github.com/SitrakaResearchAndPOC/OCXO_USRP/blob/main/gpsdo2.png" width="200" />
  <img src="https://github.com/SitrakaResearchAndPOC/OCXO_USRP/blob/main/gpsdo3.png" width="235" />
</p>

# Installation  
Just ignore docker manipulation for real manipulation
```
xhost +
```
```
docker image pull ubuntu:24.04
```
```
docker run -tid --privileged -v /dev/bus/usb:/dev/bus/usb -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v $XAUTHORITY:/home/user/.Xauthority:ro --net=host --env="DISPLAY=$DISPLAY" --env="LC_ALL=C.UTF-8" --env="LANG=C.UTF-8" --name gpsdo_03_2026 ubuntu:24.04
```
```
docker exec -ti gpsdo_03_2026 /bin/bash
```
Directly there for non docker installation
```
apt update
```
```
apt install -y git cmake build-essential libboost-all-dev     libusb-1.0-0-dev python3-dev python3-mako python3-numpy     python3-requests python3-setuptools libfftw3-dev     libcomedi-dev libgps-dev libgmp-dev swig pkg-config gedit
```
```
git clone https://github.com/EttusResearch/uhd.git
```
```
cd uhd
```
```
ls
```
```
cd ..
```
```
gedit uhd/host/lib/usrp/gps_ctrl.cpp
```
Full code is there [gps_ctrl.cpp](https://github.com/SitrakaResearchAndPOC/OCXO_USRP/blob/main/gps_ctrl.cpp)    
For futur manipulation patch is more interesting :  <br/>

<p align="center"> <img src="https://github.com/SitrakaResearchAndPOC/OCXO_USRP/blob/main/gpsdo_patch.png" alt="description" width=550 /> </p>

* STEP1 :  <br/>
Change regex use :  <br/>
```
static const std::regex gp_msg_regex("^\\$G.*$");
```
instead  <br/>
```
static const std::regex gp_msg_regex("^\\$GP.*,\\*[0-9A-F]{2}$");
```

* STEP2 :  <br/>
Before :
```
msgs[msg.substr(1, 5)] = msg;
```
add, 
```
// change GN by GP
if(msg.substr(1,2) == "GN"){ msg.replace(1, 2, "GP");}
```
Compilation of UHD  
```    
cd uhd/host/
```
```
ls
```
```
mkdir build
```
```
cd build/
```
Verify option ENABLE_PYTHON
```
cmake .. -LAH | grep -i ENABLE_PYTHON
```
Verify option ENABLE_LIBUHD
```
cmake .. -LAH | grep -i ENABLE_LIBUHD
```
Cmake before installation
```
cmake ..   -DENABLE_PYTHON=ON  -DENABLE_LIBUHD=ON -DPYTHON_EXECUTABLE=$(which python3)
```

Choose the real number core of computer on number 10
```
make -j 10
```
```
make install
```
```
ldconfig
```
Downloading Image of USRP
```
cd /usr/local/lib/uhd/utils/
```
```
ls
```
```
uhd_images_downloader 
```
Testing synchronization GPS : 
```
cd /usr/local/lib/uhd/utils/
```
```
ls
```
```
./query_gpsdo_sensors 
```
Nruradio log ( <bold>GPS ALIGN </bold> is very important): 
<p align="center"> <img src="https://github.com/SitrakaResearchAndPOC/OCXO_USRP/blob/main/log_nuradio.png" alt="description" width=550 /> </p>

Adding script bonus on PYTHON
```
gedit test_usrp_gpsdo.py
```
```
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

usrp_device = usrp.MultiUSRP("")

# Utiliser le GPSDO comme source d'horloge
usrp_device.set_clock_source("gpsdo")
usrp_device.set_time_source("gpsdo")
time.sleep(2)

# Liste des capteurs disponibles
sensor_names = usrp_device.get_mboard_sensor_names(0)
print("Capteurs disponibles :", sensor_names)

# Vérifie GPS lock proprement
if "gps_locked" in sensor_names:
    try:
        gps_sensor = usrp_device.get_mboard_sensor("gps_locked", 0)
        print(f"GPSDO lock sur satellites : {gps_sensor.value}")
    except RuntimeError as e:
        print("GPS non verrouillé (pas de fix pour le moment)")
        print("Détail :", e)
else:
    print("Capteur 'gps_locked' non disponible")

# Vérifie ref_locked
if "ref_locked" in sensor_names:
    try:
        ref_sensor = usrp_device.get_mboard_sensor("ref_locked", 0)
        print(f"ref_locked = {ref_sensor.value}")
    except RuntimeError as e:
        print("Impossible de lire ref_locked :", e)

# ------------------------------------------------------------------
# 🔥 ALIGNEMENT TEMPOREL GPSDO
# ------------------------------------------------------------------
print("\n--- Synchronisation temporelle GPSDO ---")

time.sleep(2)

usrp_device.set_time_now(uhd.types.TimeSpec(0.0))
usrp_device.set_time_next_pps(uhd.types.TimeSpec(0.0))

print("Attente du PPS GPSDO...")
time.sleep(2)

# ------------------------------------------------------------------
# 🔥 INFO GPS / PPS (STYLE UHD PROPRE)
# ------------------------------------------------------------------

print("\n--- Infos GPS / PPS ---")

try:
    gps_time = float(usrp_device.get_mboard_sensor("gps_time", 0).value)

    last_pps = int(gps_time)

    print(f"last_pps: {last_pps} vs gps: {last_pps}")

except Exception as e:
    print("Impossible de lire gps_time :", e)

print("\nPrinting available NMEA strings:")

try:
    print("GPS_GPGGA:", usrp_device.get_mboard_sensor("gps_gpgga", 0).value)
    print("GPS_GPRMC:", usrp_device.get_mboard_sensor("gps_gprmc", 0).value)
except Exception as e:
    print("NMEA non disponible :", e)

try:
    gps_time = float(usrp_device.get_mboard_sensor("gps_time", 0).value)
    print(f"GPS Epoch time at last PPS: {gps_time:.5f} seconds")
except Exception as e:
    print("GPS epoch non disponible :", e)

# ------------------------------------------------------------------
# 🔥 UHD DEVICE TIME (CORRIGÉ STYLE QUERY_SENSORS_GPSDO)
# ------------------------------------------------------------------

gps_time = float(usrp_device.get_mboard_sensor("gps_time", 0).value)

device_time = usrp_device.get_time_now().get_real_secs()

# reconstruction propre comme UHD tool (cohérent, pas FPGA brut)
absolute_time = gps_time + (device_time - int(device_time))

print(f"UHD Device time last PPS:   {gps_time:.5f} seconds")
print(f"UHD Device time right now:  {absolute_time:.5f} seconds")

print(f"PC Clock time:              {int(time.time())} seconds")

print("\nDone!")
```
```
python3 test_usrp_gpsdo.py
```
