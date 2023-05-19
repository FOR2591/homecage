# FOR2591: Homecage Monitoring System

This repository contains the software, system configurations, and 3D models presented in:

 [Towards substitution of invasive telemetry: An integrated home cage concept for unobstrusive monitoring of objective physiological parameters in rodents](https://www.biorxiv.org/content/10.1101/2023.05.12.540546v1.full)
 
## Features
* Configuration for full-speed, high resolution RGB-image capturing using a Raspberry Pi 4 with a Pi Camera 
* Software for network-integrated video monitoring
* Back- and frontend software for monitoring control
* STL-files for camera enclosures

## Setup

### Raspberry Pi
The resolution limits for photo capture need to be adjusted by using a custom bcm2835-v4l2.conf to enable the Raspberry Pi to capture high-resolution frames at 40fps using the PiCamera v2.
```
cp .installation/etc/modprobe.d/bcm2835-v4l2.conf /etc/modprobe.d/
```
### Monitoring

### Webserver
