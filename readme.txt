# OCXO JOHN WU
Conversation ouverte. 6 messages. Tous les messages ont été lus.

Aller au contenu
Utiliser Messagerie Ecole supérieure des technologies de l'information avec un lecteur d'écran
gpsdo 

1 sur 26
gpsdo
Boîte de réception

Sitraka Rakotondramanana <sitraka.rakotondramanana@esti.mg>
Pièces jointes
18 mars 2026 07:27 (il y a 1 jour)
À moi


 5 pièces jointes
  •  Analysé par Gmail

Sitraka Rakotondramanana
18 mars 2026 07:35 (il y a 1 jour)
#!/usr/bin/env python3 from uhd import usrp import time usrp_device = usrp.MultiUSRP("") # Utiliser le GPSDO comme source d'horloge usrp_device.set_clock_source

Sitraka Rakotondramanana <sitraka.rakotondramanana@esti.mg>
Pièces jointes
18 mars 2026 12:09 (il y a 22 heures)
À moi

 Une pièce jointe
  •  Analysé par Gmail

Sitraka Rakotondramanana
18 mars 2026 20:17 (il y a 14 heures)
https://fr.aliexpress.com/item/1005006345803880.html?spm=a2g0o.productlist.main.11.3d5b1PUw1PUwhF&algo_pvid=b93d7222-1923-4af4-a9f0-e6f12edf7d18&algo_exp_id=b93

Sitraka Rakotondramanana <sitraka.rakotondramanana@esti.mg>
18 mars 2026 20:19 (il y a 14 heures)
À moi

https://fr.aliexpress.com/item/1005011565578396.html?spm=a2g0o.productlist.main.13.7d40bQQebQQeuf&algo_pvid=ac548dc9-e705-4769-b8c2-75890ae36285&algo_exp_id=ac548dc9-e705-4769-b8c2-75890ae36285-12&pdp_ext_f=%7B%22order%22%3A%224%22%2C%22spu_best_type%22%3A%22price%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21USD%2111.30%215.65%21%21%2177.40%2138.70%21%402103849717738220574835623e93d0%2112000055936451158%21sea%21MG%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3A93418ddb%3Bm03_new_user%3A-29895&curPageLogUid=hMK9lZXTprls&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005011565578396%7C_p_origin_prod%3A

Sitraka Rakotondramanana <sitraka.rakotondramanana@esti.mg>
18 mars 2026 20:31 (il y a 14 heures)
À moi

Car GPS Signal Antenna Amplifier Booster with GPS Receiver + Transmitter 30DB for Phone Navigator - AliExpress 34

xhost +

docker image pull ubuntu:24.04

docker run -tid --privileged -v /dev/bus/usb:/dev/bus/usb -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v $XAUTHORITY:/home/user/.Xauthority:ro --net=host --env="DISPLAY=$DISPLAY" --env="LC_ALL=C.UTF-8" --env="LANG=C.UTF-8" --name gpsdotest_03_2026 ubuntu:24.04

docker exec -ti gpsdotest_03_2026 /bin/bash


apt update
apt install -y git cmake build-essential libboost-all-dev     libusb-1.0-0-dev python3-dev python3-mako python3-numpy     python3-requests python3-setuptools libfftw3-dev     libcomedi-dev libgps-dev libgmp-dev swig pkg-config gedit

git clone https://github.com/EttusResearch/uhd.git
cd uhd
ls
cd ..
gedit uhd/host/lib/usrp/gps_ctrl.cpp
    
    
    
cd uhd/host/
ls
mkdir build
cd build/
cmake ..
make -j 10
make install
ldconfig
clear
ls
make install
ldconfig
cd /usr/local/lib/uhd/utils/
ls
uhd_images_downloader 
ls
./query_gpsdo_sensors 
history
   
   gedit test_usrp.py
   
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


python3 test_usrp.py
GPSDO_LATEST.txt
Affichage de GPSDO_LATEST.txt en cours...
