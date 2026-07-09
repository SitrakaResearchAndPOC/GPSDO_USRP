## I. Installing tools
```
rm -rf gpsdo_usrp ; mkdir gpsdo_usrp && cd gpsdo_usrp
```
```
apt update
```
```
apt install docker.io wget
```
```
apt-get install linux-tools-common linux-tools-generic
```
```
cpupower frequency-set -g performance
```
## II. Choice Dockerfile
```
[ -f Dockerfile ] && rm -rf Dockerfile ; \
wget https://raw.githubusercontent.com/SitrakaResearchAndPOC/GPSDO_USRP/refs/heads/main/Dockerfile
```
```
docker  build -t gpsdo_usrp:v1 .
```
## III. Launching gpsdo_usrp
```
docker rm -f gpsdo_usrp 2> /dev/null ; \
docker run -tid --privileged \
  --cgroupns=host \
  --net=host \
  -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
  -v /dev:/dev \
   --device=/dev/bus/usb \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v /home/user/.Xauthority:/home/user/.Xauthority:ro \
  --tmpfs /run \
  --tmpfs /run/lock \
  --env="DISPLAY=$DISPLAY" \
  --env="LC_ALL=C.UTF-8" \
  --env="LANG=C.UTF-8" \
  --env="NAME_PLUTO=pluto" \
  --cap-add=sys_nice \
  --cap-add=ipc_lock \
  --ulimit rtprio=99 \
  --ulimit memlock=-1 \
  --volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket \
  --name srsran_pluto \
  --hostname gpsdo_usrp \
  gpsdo_usrp:v1
```
## IV. check gpsdo_usrp

```
docker exec -ti gpsdo_usrp bash -c 'uhd_find_devices'
```
```
docker exec -ti gpsdo_usrp bash -c 'uhd_usrp_probe'
```

```
docker exec -ti gpsdo_usrp bash -c 'query_gpsdo_sensors'
```

