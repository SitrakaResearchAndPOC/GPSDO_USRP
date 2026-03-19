# OCXO JOHN WU
# GPDO integrated on USRP
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
* STEP1 :
Change regex use :  <br/>
```
static const std::regex gp_msg_regex("^\\$G.*$");
```
instead  <br/>
```
static const std::regex gp_msg_regex("^\\$GP.*,\\*[0-9A-F]{2}$");
```

* STEP2
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
```
cmake ..
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
Adding script bonus on PYTHON
```
gedit test_usrp.py
```
``` 
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
```
```
python3 test_usrp.py
```

Affichage de GPSDO_LATEST.txt en cours...
