# Hybrid3DPositioning
Hybrid RF-Acoustic Positioning embedded software and python implementation.

## System overview
Hybrid RF/acoustic ranging measurements are used to perform indoor 3D positioning. The system consists of two entities: mobile node and a beacon. A fixed beacon sends an audio chirp and RF wake-up signal. Consequently mobile nodes all awake simultaneously triggered by the RF signal and sample audio for a limited amount of time. The ranging information is comprised in the received audio signal and depends on the distance to the beacon.
![image](https://user-images.githubusercontent.com/31063583/117812706-6cfd2280-b262-11eb-8aa0-0e14c241f05e.png)

For more information on the distance calculations, we refer to: https://doi.org/10.1109/LSENS.2020.2990213


## Embedded software
The softiware is written for the CC1310 Ultra-Low-Power Sub-1 Ghz Wireless microcontrollers. In the repository, two folders can be found, representing the mobile node (RxTx) and beacon (TxRx). To obtain low power, Sensor Controller Interface (SCOF) Driver is used. Correct pinout can be found in the main and scif.h files.

## 3D positioning optimisation algorithms

The main.py file consists the necessary code to steer four beacons and receive chirp data of the mobile node. The distances are calculated in this file as well and stored in the correct folder.
The data folder contains the measured distances for 150 positions in the Techtile setup.
A python implementation of five positioning algorithms can be found in locfunc.py
Plotting.py is used to create plotly figures of the setup.
Note that some paths need to be adapted to let the code work correctly.
