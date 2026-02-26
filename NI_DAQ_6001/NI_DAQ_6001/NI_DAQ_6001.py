
# Import various modules

from ast import Try, TryStar
import os
from pickle import FALSE
import math
import numpy
import NI_DAQ_Lib
import Plotting
import NI_DAQ_Hacking

# The aim of this script is to establish comms with NI-DAQ USB 6001
# Official Documentation: https://nidaqmx-python.readthedocs.io/en/stable/
# Examples with explanation: https://nidaqmx-python.readthedocs.io/en/stable/#python-examples
# Nice introduction: https://www.halvorsen.blog/documents/programming/python/resources/powerpoints/DAQ%20with%20Python.pdf
# Examples online: https://github.com/ni/nidaqmx-python/tree/master
# R. Sheehan 21 - 11 - 2025

MOD_NAME_STR = "NI_DAQ_600x"

def main():
    pass

if __name__ == '__main__':
    main()

    pwd = os.getcwd() # get current working directory

    print(pwd)
    
    #NI_DAQ_Hacking.Making_Waves()

    #NI_DAQ_Hacking.AO_Write_Test()
    
    #NI_DAQ_Hacking.AI_Read_Test()
    
    #NI_DAQ_Hacking.AO_AI_Loopback_Test()

    #NI_DAQ_Hacking.AI_Read_Multiple_Channels()

    #NI_DAQ_Hacking.NI_DAQ_String_Hacking()

    #NI_DAQ_Hacking.NI_DAQ_SR_Extract_Testing()

    #NI_DAQ_Hacking.AI_Read_Multiple_Channels_with_Clock_Test()

    #NI_DAQ_Hacking.DC_Sweep_Diode()

    #NI_DAQ_Hacking.AO_Waveform_Write_Test()

    #NI_DAQ_Hacking.AI_Waveform_Read_Test()

    #NI_DAQ_Lib.AI_Timed_DC_Measurement('Dev2/ai0:3', 'Dev2', 1, 5, loud = True)

    #NI_DAQ_Lib.AO_DC_Output('Dev2/ao0','Dev2',[0.0, 2.7])
    
    NI_DAQ_Lib.AO_AC_Output('Dev2/ao1', 'Dev2', 'Triangle Unipolar', 50, 2, 7.0, 0.0)
    
    #NI_DAQ_Lib.AO_Random_Output('Dev2/ao0', 'Dev2', 'PRBS', 0.5/1000.0, 7)