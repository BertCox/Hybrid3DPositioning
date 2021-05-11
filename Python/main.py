#  ____  ____      _    __  __  ____ ___
# |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
# | | | | |_) |  / _ \ | |\/| | |  | | | |
# | |_| |  _ <  / ___ \| |  | | |__| |_| |
# |____/|_| \_\/_/   \_\_|  |_|\____\___/
#                           research group
#                             dramco.be/
#
#  KU Leuven - Technology Campus Gent,
#  Gebroeders De Smetstraat 1,
#  B-9000 Gent, Belgium
#
#         File: main.py
#      Created: 2021-02-23
#       Author: Bert Cox
#      Version: 0.1
#
#  Description:
#
#  Create chirp signal
#  NI DAQ USB 6215 chirp write to the 4 channels
#  Read UART data of distance data calculated at the CC1310
#  Store the distances to a CSV file
#
#  License L (optionally)
#

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Libraries --------------------------------------------------------------------------------------------------
import nidaqmx
from nidaqmx import stream_writers
from nidaqmx.constants import Slope, Edge, AcquisitionType
import numpy as np
import scipy as sci
from scipy.signal import chirp
import serial
from DigitalChirp import dataChirp
import time
import csv

# declaration of variables -----------------------------------------------------------------------------------
start_frequency = 45000                             # max frequency of chirp
stop_frequency = 25000                              # min frequency of chirp
chirp_sample_length = 7500                          # amount of samples for the chirp
chirp_duration = 0.03                               # duration of chirp signal
DAQ_speed = chirp_sample_length/chirp_duration      # sampling speed at the DAQ
position = "Position24"
file_name = position + ".csv"
path = 'C:\\Users\\coxbe\\Box\\KU Leuven\\PhD\\Papers\\IPIN2021\\Code\\Python\\Data2\\' + position + '\\'
CHIRPDATASIZE = 480
SAMPLEDATASIZE = 16
SAMPLEBITSIZE  = 512
CHIRPDATAPAIRS = int((CHIRPDATASIZE/SAMPLEDATASIZE))
mask = 0x80000000
distanceCalculated = 0
# setting up serial communication -----------------------------------------------------------------------------
ser = serial.Serial(
    port='COM13',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)
print("connected to: " + ser.portstr)
import matplotlib.pyplot as plt
import time


# create chirp signal -----------------------------------------------------------------------------------------
t = np.linspace(0, chirp_duration, chirp_sample_length)
chirp_signal = (sci.signal.chirp(t, start_frequency, chirp_duration, stop_frequency, method='linear')*2.5)+2.5
# set first and last bit to 0
chirp_signal[0] = 0
chirp_signal[len(chirp_signal)-1] = 0

print("Chirp created")

# check if received value is int
def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


# calculate the distance of the received UART data -----------------------------------------------------------
def calculatedistance(array):
    reference_datachirp = dataChirp.copy()
    result = 0
    index = 0
    u = 0
    v = 0
    w = 0
    for u in range(SAMPLEBITSIZE):
        for v in range(CHIRPDATAPAIRS):
            temp_result = 0
            # Hamming weight calculations
            for w in range(SAMPLEDATASIZE):
                temp_result += bin(~(reference_datachirp[(v * SAMPLEDATASIZE + w)] ^ array[w])).count('1')
                # bitshift
                reference_datachirp[(v * SAMPLEDATASIZE + w)] <<= 1
                # masking is necessary in python: bit shift of Long creates 33 bit number otherwise
                reference_datachirp[(v * SAMPLEDATASIZE + w)] &= (2**32-1)
                if (reference_datachirp[(v * SAMPLEDATASIZE + w) + 1] & mask) == mask:
                    reference_datachirp[(v * SAMPLEDATASIZE + w)] += 1

            if temp_result >= result:
                index = (u + (v * SAMPLEBITSIZE))
                result = temp_result
    distance = (14488 - index) * 0.000686
    return distance

# test_distance = calculatedistance(test_chirp)
# print(test_distance)
# Main ----------------------------------------------------------------------------------------------------
# discard first 3 measurements
ADCBinaryDataULong = [*range(0, 16)]
discard = 0
while discard < 4:
    with nidaqmx.Task() as writeTaskDiscard:
        deviceDiscard = "Dev1/ao0"
        writeTaskDiscard.ao_channels.add_ao_voltage_chan(deviceDiscard)
        writeTaskDiscard.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev1/PFI1",
                                                                    trigger_edge=Edge.RISING)
        writeTaskDiscard.timing.cfg_samp_clk_timing(rate=DAQ_speed, active_edge=Edge.RISING,
                                                sample_mode=AcquisitionType.FINITE,
                                                samps_per_chan=chirp_sample_length)

        # write the data to  the correct channel
        write = stream_writers.AnalogSingleChannelWriter(writeTaskDiscard.out_stream, auto_start=True)
        write.write_many_sample(chirp_signal, timeout=100)
        writeTaskDiscard.wait_until_done(timeout=100)
        writeTaskDiscard.stop()
        fault_distance = True
        h = 0
        for h in range(16):
            ser_long = ser.readline()
            if isint(ser_long):
                ADCBinaryDataULong[h] = int(ser_long[0:(len(ser_long) - 2)])
                # print(ADCBinaryDataULong[h])
            else:
                ADCBinaryDataULong[h] = 0
                fault_distance = False
                break
        if fault_distance:
            distanceCalculated = calculatedistance(ADCBinaryDataULong)
            print('Discard: ' + str(distanceCalculated))
    discard += 1

i = 1
k = 2
iteration = 0
while i < 3:
    with nidaqmx.Task() as writeTaskOutput1, nidaqmx.Task() as writeTaskOutput2:

        # create an output channel 1
        device1 = "Dev1/ao" + str(i)
        speaker = "Speaker" + str(k)
        # k += 1
        writeTaskOutput1.ao_channels.add_ao_voltage_chan(device1)

        # select DIGITAL signal to trigger on
        writeTaskOutput1.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev1/PFI1",
                                                                        trigger_edge=Edge.RISING)
        writeTaskOutput1.timing.cfg_samp_clk_timing(rate=DAQ_speed, active_edge=Edge.RISING,
                                                    sample_mode=AcquisitionType.FINITE,
                                                    samps_per_chan=chirp_sample_length)

        # write the data to  the correct channel
        write = stream_writers.AnalogSingleChannelWriter(writeTaskOutput1.out_stream, auto_start=True)
        write.write_many_sample(chirp_signal, timeout=100)
        writeTaskOutput1.wait_until_done(timeout=100)
        writeTaskOutput1.stop()
        h = 0
        fault_distance = True
        # receive UART data from CC1310
        for h in range(16):
            ser_long = ser.readline()
            if isint(ser_long):
                ADCBinaryDataULong[h] = int(ser_long[0:(len(ser_long) - 2)])
                # print(ADCBinaryDataULong[h])
            else:
                ADCBinaryDataULong[h] = 0
                fault_distance = False
                break
        if fault_distance:
            distanceCalculated = calculatedistance(ADCBinaryDataULong)
            print(speaker + ': ' + str(distanceCalculated))
            with open(path + speaker + file_name, "a", newline='') as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow([distanceCalculated])
        iteration += 1
        print(iteration)
        # # create an output channel 2
        # device2 = "Dev2/ao" + str(i)
        # speaker = "Speaker" + str(k)
        # k += 1
        # # print(device2)
        # writeTaskOutput2.ao_channels.add_ao_voltage_chan(device2)
        #
        # # select DIGITAL signal to trigger on
        # writeTaskOutput2.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev2/PFI1",
        #                                                                 trigger_edge=Edge.RISING)
        # writeTaskOutput2.timing.cfg_samp_clk_timing(rate=DAQ_speed, active_edge=Edge.RISING,
        #                                             sample_mode=AcquisitionType.FINITE,
        #                                             samps_per_chan=chirp_sample_length)
        #
        # # write the data to the correct channel
        # write = stream_writers.AnalogSingleChannelWriter(writeTaskOutput2.out_stream, auto_start=True)
        # write.write_many_sample(chirp_signal, timeout=100)
        # writeTaskOutput2.wait_until_done(timeout=100)
        # writeTaskOutput2.stop()
        # h = 0
        # fault_distance = True
        # # receive UART data from CC1310
        # for h in range(16):
        #     ser_long = ser.readline()
        #     if isint(ser_long):
        #         ADCBinaryDataULong[h] = int(ser_long[0:(len(ser_long) - 2)])
        #     else:
        #         ADCBinaryDataULong[h] = 0
        #         fault_distance = False
        #         break
        # if fault_distance:
        #     distanceCalculated = calculatedistance(ADCBinaryDataULong)
        #     print(speaker + ': ' + str(distanceCalculated))
        #     with open(path + speaker + file_name, 'a', newline='') as f:
        #         writer = csv.writer(f, delimiter=",")
        #         writer.writerow([distanceCalculated])
        # i += 1
        # if (i == 2):
        #     i = 0
        #     k = 0
        #     iteration += 1
        #     print(iteration)