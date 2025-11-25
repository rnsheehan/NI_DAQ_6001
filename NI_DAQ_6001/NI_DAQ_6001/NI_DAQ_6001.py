
# Import various modules

from ast import Try
import os
import sys
import glob
import re
import serial
import pyvisa
import time
import numpy
import math
import nidaqmx
import Common
import Plotting

# The aim of this script is to establish comms with NI-DAQ USB 6001
# Official Documentation: https://nidaqmx-python.readthedocs.io/en/stable/
# Examples with explanation: https://nidaqmx-python.readthedocs.io/en/stable/#python-examples
# Nice introduction: https://www.halvorsen.blog/documents/programming/python/resources/powerpoints/DAQ%20with%20Python.pdf
# Examples online: https://github.com/ni/nidaqmx-python/tree/master
# R. Sheehan 21 - 11 - 2025

MOD_NAME_STR = "NI_DAQ_600x"

def AO_Write_Test():

    # check that your NI-DAQ is being controlled by Python by getting AO channel to write an output
    # R. Sheehan 21 - 11 - 2025

    FUNC_NAME = ".AO_Write_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME
    
    try:
        task = nidaqmx.Task()
        
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        
        task.start()
        
        voltage = 2.7        
        task.write(voltage)
        time.sleep(5)
        
        voltage = -4.2
        task.write(voltage)
        time.sleep(5)
        
        voltage = 0.0
        task.write(voltage)
        time.sleep(5)

        task.stop()
        
        task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)
        
def AI_Read_Test():
    
    # check that your NI-DAQ is being controlled by Python by getting AI channel to read an output
    # R. Sheehan 21 - 11 - 2025

    FUNC_NAME = ".AI_Read_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        task = nidaqmx.Task()
        
        task.ai_channels.add_ai_voltage_chan('Dev1/ai0')
        
        task.start()
        
        N = 61
        count = 0
        while count < N:
            value = task.read()
            print(value)
            time.sleep(1)
            count = count + 1

        task.stop()
        
        task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AO_AI_Loopback_Test():
    
    # check that your NI-DAQ is being controlled by Python
    # write an AO value
    # read the same voltage value using AI
    # R. Sheehan 21 - 11 - 2025

    FUNC_NAME = ".AO_AI_Loopback_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        # Configure Analog Output
        ao_task = nidaqmx.Task()
        ao_task.ao_channels.add_ao_voltage_chan('Dev1/ao0', min_val = -10, max_val = +10)
        ao_task.start()
        
        # Configure Analog Input
        from nidaqmx.constants import (TerminalConfiguration)
        ai_task = nidaqmx.Task()        
        ai_task.ai_channels.add_ai_voltage_chan('Dev1/ai0',terminal_config=TerminalConfiguration.DIFF, min_val = -10, max_val = +10)        
        #ai_task.ai_channels.add_ai_voltage_chan('Dev1/ai0')        
        ai_task.start()
        
        # output the voltage value
        voltage = 7.6234
        ao_task.write(voltage)   
        print("Set voltage:",voltage," (V)")
        
        # read some data
        N = 21
        count = 0
        read_vals = numpy.array([]) # instantiate an empty numpy array
        while count < N:
            value = ai_task.read()
            read_vals = numpy.append(read_vals, value)
            time.sleep(0.5)
            count = count + 1
        avg = numpy.mean(read_vals)
        stdev = numpy.std(read_vals, ddof = 1)
        upper = avg+stdev
        lower = avg-stdev
        in_range = True if voltage < upper and voltage > lower else False
        print("Average of ",N,"reads: %(v1)0.04f +/- %(v2)0.04f (V)"%{"v1":avg, "v2":stdev})
        print("Upper bound: %(v1)0.04f (V)"%{"v1":upper})
        print("Lower bound: %(v1)0.04f (V)"%{"v1":lower})
        if in_range:
            print("Output is accurate to mV level")    
        
        # change the voltage value
        voltage = -4.3271       
        ao_task.write(voltage)
        print("\nSet voltage:",voltage," (V)")
        
        # read some more data
        N = 21
        count = 0
        read_vals = numpy.array([]) # instantiate an empty numpy array
        while count < N:
            value = ai_task.read()
            read_vals = numpy.append(read_vals, value)
            time.sleep(0.5)
            count = count + 1
        avg = numpy.mean(read_vals)
        stdev = numpy.std(read_vals, ddof = 1)
        upper = avg+stdev
        lower = avg-stdev
        in_range = True if voltage < upper and voltage > lower else False
        print("Average of ",N,"reads: %(v1)0.04f +/- %(v2)0.04f (V)"%{"v1":avg, "v2":stdev})
        print("Upper bound: %(v1)0.04f (V)"%{"v1":upper})
        print("Lower bound: %(v1)0.04f (V)"%{"v1":lower})
        if in_range:
            print("Output is accurate to mV level")    
        
        # reset to zero
        voltage = 0.0        
        ao_task.write(voltage)    
        
        # close all tasks
        ao_task.stop()
        ai_task.stop()
        
        ao_task.close()
        ai_task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AI_Read_Multiple_Channels():

    # Need to know how to read on multiple analog inputs
    # Need to know how to configure correct sample rate for multiple analog inputs
    # R. Sheehan 25 - 11 - 2025

    FUNC_NAME = ".AO_AI_Loopback_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        from nidaqmx.constants import TerminalConfiguration, AcquisitionType, READ_ALL_AVAILABLE

        AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
        AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

        # Sample Rate is determined by the number of channels being used
        # SR per channel = SR / No. Channels
        # Sample Rate is determined by the terminal configuration
        # single-ended => readings taken at SR per channel
        # differential => readings taken on both channels at 0.5 * SR per channel

        # Configure Analog Output
        ao_task = nidaqmx.Task()
        ao_chn_str = 'Dev2/ao0:1'
        ao_task.ao_channels.add_ao_voltage_chan(ao_chn_str, min_val = -10, max_val = +10)
        sample_rate = AO_SR_MAX / 2; 
        ao_task.timing.cfg_samp_clk_timing(sample_rate, sample_mode = AcquisitionType.FINITE, no_samples = 500)
        ao_task.start()
        
        # Configure Analog Input
        from nidaqmx.constants import (TerminalConfiguration)
        ai_task = nidaqmx.Task()        
        ai_chn_str = 'Dev2/ai0:3'
        ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config=TerminalConfiguration.DIFF, min_val = -10, max_val = +10)
        ai_task.start()
        
        # output the voltage value
        voltage = [-5.67, 2.345]
        ao_task.write(voltage)   
        print("Set voltage:",voltage," (V)")
        
        # read some data
        N = 21
        count = 0
        read_vals = numpy.array([]) # instantiate an empty numpy array
        while count < N:
            value = ai_task.read()
            #read_vals = numpy.append(read_vals, value)
            print(value)
            time.sleep(0.5)
            count += 1

        # reset to zero
        voltage = numpy.arange(0.0,2)        
        ao_task.write(voltage)    
        
        # close all tasks
        ao_task.stop()
        ai_task.stop()
        
        ao_task.close()
        ai_task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def Bitwise_Operator_Hacking():

    # Playing with different methods for determining the numbers of channels connected

    AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
    AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

    # Bitwise operators, because why not
    # https://wiki.python.org/moin/BitwiseOperators
    print("The Number: ",AO_SR_MAX)
    print("Divide by 2: ",AO_SR_MAX>>1)
    print("Divide by 4: ",AO_SR_MAX>>2)
    print("Divide by 8: ",AO_SR_MAX>>3)
    print("Multiply by 2: ",AO_SR_MAX<<1)
    print("Multiply by 4: ",AO_SR_MAX<<2)
    print("Multiply by 8: ",AO_SR_MAX<<3)
    print("\nThe Number: ",AI_SR_MAX)
    print("Divide by 2: ",AI_SR_MAX>>1)
    print("Divide by 4: ",AI_SR_MAX>>2)
    print("Divide by 8: ",AI_SR_MAX>>3)
    print("Multiply by 2: ",AI_SR_MAX<<1)
    print("Multiply by 4: ",AI_SR_MAX<<2)
    print("Multiply by 8: ",AI_SR_MAX<<3)

def NI_DAQ_String_Hacking():
    
    # Playing with different methods for determining the numbers of channels connected
    # Various methods for representing the channel naming string
    # ai_chn_str = 'Dev2/ai0:x', x = 1, 2, 3, 4, 5, 6, 7 to open all channels in single-ended mode
    # ai_chn_str = 'Dev2/ai0:x', x = 1, 2, 3 to open all channels in differential mode
    # The following is also possible
    # ai_chn_str = 'Dev2/ai0, Dev2/ai1, Dev2/ai4, Dev2/ai7'
    # Need to count the number of channels being accessed

    AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
    AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

    # No commas, single semi-colon
    ai_chn_str = 'Dev2/ai0:7'
    print()
    print(ai_chn_str)
    #print(int(ai_chn_str.split(':')[-1]))    
    #print(ai_chn_str.replace('Dev2/',''))
    #print( Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) )
    #print( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) 
    #print( max ( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) )
    print("No. channels: ", 1 + max ( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) )
    print("Sample Rate per channel: ", AI_SR_MAX / ( 1 + max ( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) ) )

    # No semi-colons, multiple commas
    ai_chn_str = 'Dev2/ai0, Dev2/ai1, Dev2/ai4, Dev2/ai7'
    print()
    print(ai_chn_str)
    #print(ai_chn_str.replace('Dev2/',''))
    #print( Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) )
    #print( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) 
    #print( len ( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) )
    print("No. channels: ", len ( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) )
    print("Sample Rate per channel: ", AI_SR_MAX / ( len ( list ( map ( int, Common.extract_values_from_string( ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) ) )

    # This works but how do you handle general cases like the one below? 
    # mix semi-colon, commas

    # re.findall(r"[-+]?\d+[\.]?\d*", the_string)

    ai_chn_str = 'Dev2/ai0:3, Dev2/ai4, Dev2/ai6'
    print()
    print(ai_chn_str)
    print(ai_chn_str.replace('Dev2/','') )
    print( re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) )
    print( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) 

    ai_chn_str = 'Dev2/ai0:2, Dev2/ai5:7'
    print()
    print(ai_chn_str)
    print(ai_chn_str.replace('Dev2/','') )
    print( re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) )
    print( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) )
    
    ai_chn_str = 'Dev2/ai3:6'
    print()
    print(ai_chn_str)
    print(ai_chn_str.replace('Dev2/','') )
    print( re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) )
    print( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) )

def main():
    pass

if __name__ == '__main__':
    main()

    pwd = os.getcwd() # get current working directory

    print(pwd)
    
    #AO_Write_Test()
    
    #AI_Read_Test()
    
    #AO_AI_Loopback_Test()

    #AI_Read_Multiple_Channels()

    NI_DAQ_String_Hacking()