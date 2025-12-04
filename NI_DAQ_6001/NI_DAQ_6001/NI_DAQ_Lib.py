"""
Python library for interfacing to the NI-DAQ USB-600x

R. Sheehan 21 - 11 - 2025
"""

# The aim is to establish comms with NI-DAQ USB 6001
# It appears that the code will also work for other NI-DAQ variants if configured correctly
# Official Documentation: https://nidaqmx-python.readthedocs.io/en/stable/
# Examples with explanation: https://nidaqmx-python.readthedocs.io/en/stable/#python-examples
# Nice introduction: https://www.halvorsen.blog/documents/programming/python/resources/powerpoints/DAQ%20with%20Python.pdf
# Examples online: https://github.com/ni/nidaqmx-python/tree/master

# Originally I was going to write a class that would interface with the NI-DAQ, however, given that nidaqmx already defines a class for interfacing to the NI-DAQ any
# class I would write would basically be a worse version of the nidaqmx class, essentially just a wrapper that would be less flexible than nidaqmx.
# Instead of writing an inferior wrapper class I'm going to implement a library performs some common tasks that the NI-DAQ is used for
# R. Sheehan 3 - 12 - 2025

# import required libraries
import os

import nitypes.waveform

os.environ["NIDAQMX_ENABLE_WAVEFORM_SUPPORT"] = "1"

import re
import math
import numpy
import time
import nidaqmx
import nitypes
import datetime
import matplotlib.pyplot as plot
import Sweep_Interval
import Plotting

MOD_NAME_STR = "NI_DAQ_Lib"
AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

# Basic Test and Operation Routines
# Use these to check basic DAQ communication and functionality

def AO_Write_Test():
    """
    check that your NI-DAQ is being controlled by Python by getting AO channel to write an output
    R. Sheehan 21 - 11 - 2025
    """

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
    """
    check that your NI-DAQ is being controlled by Python by getting AI channel to read an output
    R. Sheehan 21 - 11 - 2025
    """

    FUNC_NAME = ".AI_Read_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        task = nidaqmx.Task()
        
        task.ai_channels.add_ai_voltage_chan('Dev2/ai0')
        
        task.start()
        
        N = 21
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
    """
    check that your NI-DAQ is being controlled by Python
    write an AO value
    read the same voltage value using AI
    R. Sheehan 21 - 11 - 2025
    """

    FUNC_NAME = ".AO_AI_Loopback_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        # Configure Analog Output
        ao_task = nidaqmx.Task()
        ao_task.ao_channels.add_ao_voltage_chan('Dev2/ao0', min_val = -10, max_val = +10)
        ao_task.start()
        
        # Configure Analog Input
        from nidaqmx.constants import (TerminalConfiguration)
        ai_task = nidaqmx.Task()        
        ai_task.ai_channels.add_ai_voltage_chan('Dev2/ai0',terminal_config=TerminalConfiguration.DIFF, min_val = -10, max_val = +10)        
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

def AI_Read_Multiple_Channels_Test():
    """
    Need to know how to read on multiple analog inputs
    Need to know how to configure correct sample rate for multiple analog inputs
    R. Sheehan 25 - 11 - 2025
    """

    FUNC_NAME = ".AI_Read_Multiple_Channels_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        #from nidaqmx.constants import TerminalConfiguration, AcquisitionType, READ_ALL_AVAILABLE, Edge

        # Sample Rate is determined by the number of channels being used
        # SR per channel = SR / No. Channels
        # Sample Rate is determined by the terminal configuration
        # single-ended => readings taken at SR per channel
        # differential => readings taken on both channels at 0.5 * SR per channel

        dev_name = 'Dev1'

        # Configure Analog Output
        ao_task = nidaqmx.Task()
        ao_chn_str = 'Dev1/ao0:1'
        ao_task.ao_channels.add_ao_voltage_chan(ao_chn_str, min_val = -10, max_val = +10)
        ao_SR, ao_no_ch = Extract_Sample_Rate(ao_chn_str, dev_name)
        #ao_task.timing.cfg_samp_clk_timing(sample_rate, sample_mode = AcquisitionType.FINITE, no_samples = 500)
        ao_task.start()
        
        # Configure Analog Input
        #from nidaqmx.constants import (TerminalConfiguration)
        ai_task = nidaqmx.Task()        
        ai_chn_str = 'Dev1/ai0:3'
        ai_SR, ai_no_ch = Extract_Sample_Rate(ai_chn_str, dev_name)
        ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, min_val = -10, max_val = +10)
        ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan = ai_SR>>2, 
                                           active_edge = nidaqmx.constants.Edge.RISING)
        # It seems that source = "" chooses the default onboard clock, which afaik is equivalent to SampleTimingType.SAMPLE_CLOCK
        ai_task.start()

        # How to assign the SR? 
        #ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = AcquisitionType.FINITE, no_samples = ai_SR)
        
        # output the voltage value
        #voltage = [-5.67, 2.345]
        voltage = [5.67, -2.345]
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
        voltage = [0.0, 0.0]        
        ao_task.write(voltage)    
        
        # close all tasks
        ao_task.stop()
        ai_task.stop()
        
        ao_task.close()
        ai_task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AI_Read_Multiple_Channels_with_Clock_Test():

    """
    Need to know how to read on multiple analog inputs
    Need to know how to configure correct sample rate for multiple analog inputs
    R. Sheehan 27 - 11 - 2025
    """

    FUNC_NAME = ".AI_Read_Multiple_Channels_with_Clock_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        #from nidaqmx.constants import TerminalConfiguration, AcquisitionType, Edge, SampleTimingType

        # for more info on nidaqmx.constants see https://nidaqmx-python.readthedocs.io/en/stable/constants.html#

        # Sample Rate is determined by the number of channels being used
        # SR per channel = SR / No. Channels
        # Sample Rate is determined by the terminal configuration
        # single-ended => readings taken at SR per channel
        # differential => readings taken on both channels at 0.5 * SR per channel

        dev_name = 'Dev1'

        # Configure Analog Output
        ao_task = nidaqmx.Task()
        ao_chn_str = 'Dev1/ao0:1'
        ao_task.ao_channels.add_ao_voltage_chan(ao_chn_str, min_val = -10, max_val = +10)
        ao_SR, ao_no_ch = Extract_Sample_Rate(ao_chn_str, dev_name)
        
        # Configure Analog Input
        ai_task = nidaqmx.Task()        
        ai_chn_str = 'Dev1/ai0:2'
        ai_SR, ai_no_ch = Extract_Sample_Rate(ai_chn_str, dev_name, True)
        ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, min_val = -10, max_val = +10)
        ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan = ai_SR>>4, active_edge = nidaqmx.constants.Edge.RISING)
        # It seems that source = "" chooses the default onboard clock, which afaik is equivalent to nidaqmx.constants.SampleTimingType.SAMPLE_CLOCK

        ao_task.start()
        ai_task.start()
        
        # output the voltage value
        #voltage = [-5.67, 2.345]
        voltage = [5.67, -2.345]
        ao_task.write(voltage)   
        print("Set voltage:",voltage," (V)")
        
        # read some data
        # documentation for read https://nidaqmx-python.readthedocs.io/en/stable/task.html#nidaqmx.task.InStream.read
        data = ai_task.read(nidaqmx.constants.READ_ALL_AVAILABLE)

        print("ai SR = ",ai_SR,' Hz => dT = ',1.0 / float(ai_SR),' s')
        if ai_no_ch == 1:
            print("samps_per_chan = ",len(data))
        else:
            for i in range(0, ai_no_ch, 1):
                print("samps_per_chan = ",len(data[i]))

        # reset to zero
        voltage = [0.0, 0.0]        
        ao_task.write(voltage)    
        
        # close all tasks
        ao_task.stop()
        ai_task.stop()
        
        ao_task.close()
        ai_task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def DC_Sweep_Diode_Test():
    """
    Perform a single channel DC sweep
    the kind that's needed to characterise a diode
    need to add current amplifier circuit to NI-DAQ output
    R. Sheehan 2 - 12 - 2025
    """

    # Assumes ao0 is sweeping, ao1 is fixed
    # Assumes differential read on all channels
    # Assumes ai0 reads Vset, ai1 reads voltage drop across Rsense, ai2 reads voltage drop across diode

    # Current amplifier based on perfect transistor is assumed to be connected to both ao channels
    # If current amplifier is powered through Ni-DAQ +5V output current saturates around 80 (mA)
    # Need external power source in order to go beyound this
    # Conclusion NI-DAQ not really suitable for driving DC circuits

    FUNC_NAME = ".DC_Sweep_Diode_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        #from nidaqmx.constants import TerminalConfiguration, AcquisitionType, Edge, SampleTimingType

        # for more info on nidaqmx.constants see https://nidaqmx-python.readthedocs.io/en/stable/constants.html#

        # Sample Rate is determined by the number of channels being used
        # SR per channel = SR / No. Channels
        # Sample Rate is determined by the terminal configuration
        # single-ended => readings taken at SR per channel
        # differential => readings taken on both channels at 0.5 * SR per channel

        dev_name = 'Dev2'

        # Configure Analog Output
        ao_task = nidaqmx.Task()
        ao_chn_str = dev_name + '/ao0:1'
        ao_task.ao_channels.add_ao_voltage_chan(ao_chn_str, min_val = -10, max_val = +10)
        ao_SR, ao_no_ch = Extract_Sample_Rate(ao_chn_str, dev_name)
        
        # Configure Analog Input
        ai_task = nidaqmx.Task()        
        ai_chn_str = dev_name + '/ai0:3'
        ai_SR, ai_no_ch = Extract_Sample_Rate(ai_chn_str, dev_name)
        ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, 
                                                min_val = -10, max_val = +10)
        ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, 
                                           samps_per_chan = ai_SR>>1, active_edge = nidaqmx.constants.Edge.RISING)

        # reset to zero
        # voltage = [0.0, 0.0]      
        # ao_task.write(voltage)
        # time.sleep(0.5)        

        PERFORM_SAMPLE_READ = False

        if PERFORM_SAMPLE_READ:

            # Assign single voltage from analog out
            # Read the result upon input

            Vset = 1.0
            Rs = 10.1 / 1000.0 # sense resistance in units of kOhm

            ao_task.start()
            ai_task.start()

            # set fixed output
            voltage = [Vset, 0.0]      
            ao_task.write(voltage)
            time.sleep(1.0)

            # perform sample read
            # possible issue with how multiple sequential reads to be performed
            # might need to stop / start task with each read
            #data = ai_task.read(nidaqmx.constants.READ_ALL_AVAILABLE)
            data = ai_task.read(ai_SR>>1)

            print("no. meas taken per channel: ",len(data[0]))
            for i in range(0, ai_no_ch, 1):
                avg = numpy.mean(data[i])
                stdev = numpy.std(data[i], ddof = 1)
                print("ai%(v1)d: %(v2)0.5f +/- %(v3)0.5f (V)"%{"v1":i, "v2":avg, "v3":stdev})
            print()
            Ival = numpy.mean(data[1]) / Rs
            Vval = numpy.mean(data[2])
            print("Diode Current: %(v1)0.3f (mA), Diode Voltage: %(v2)0.3f (V)"%{"v1":Ival, "v2":Vval})

            # reset to zero
            voltage = [0.0, 0.0]
            ao_task.write(voltage)    
        
            # close all tasks
            ao_task.stop()
            ai_task.stop()

        # Perform Multiple Reads
        PERFORM_MULTIPLE_READS = True

        if PERFORM_MULTIPLE_READS:
            # perform the DC sweep, assumes that current amplifier is in place
            Vlow = 0.0
            Vhigh = 3.0
            N_dV = 20
            Rs = 10.1 / 1000.0 # sense resistance in units of kOhm
        
            interval = Sweep_Interval.SweepSpace(N_dV, Vlow, Vhigh)

            # reset the output voltage
            ao_task.start()
            ao_task.write([0.0, 0.0])
            ao_task.stop()

            Vset = interval.start
            count = 0
            while count < interval.Nsteps:
                # engage the analog output
                ao_task.start()  
                ao_task.write([Vset, 0.0])
                time.sleep(1.0)
                ao_task.stop()

                # read data using analog input
                ai_task.start()
                # no of smpls per channel must be the same as that declared when calling cfg_samp_clk_timing
                # at this point you cannot read less samples than you've already declared
                # needless to say that you also can't read more samples than you've previously declared
                data = ai_task.read(ai_SR>>1) 
                #data = ai_task.read(nidaqmx.constants.READ_ALL_AVAILABLE)
                ai_task.stop()

                # Do some data processing
                daqVset = numpy.mean(data[0])
                Ival = numpy.mean(data[1]) / Rs
                Vval = numpy.mean(data[2])
                #print("Samples per channel: %(v1)d, Samples Read: %(v2)d"%{"v1":ai_SR>>1, "v2":len(data[1])})
                print("Desired Vset: %(v4)0.3f (V), Actual Vset: %(v3)0.3f (V), I_{diode}: %(v1)0.3f (mA), V_{diode}: %(v2)0.3f (V)"%{"v4":Vset, "v3":daqVset, "v1":Ival, "v2":Vval})

                Vset += interval.delta
                count += 1

            # reset the output voltage
            ao_task.start()
            ao_task.write([0.0, 0.0])
            ao_task.stop()
        
        ao_task.close()
        ai_task.close()

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AO_AI_Waveform_Write_Read_Test():
    """
    Configure AO to write some waveform with some frequency and amplitude
    Configure AI to read the waveform and generate a plot of the data

    R. Sheehan 3 - 12 - 2025
    """

    # Go through the github examples and extract out what you need
    # It works the same way as it does in LabVIEW
    # You generate a waveform of amplitudes assuming a certain sample rate and deltaT
    # AO can then generate the waveform as required, exither continuously or finitely

    FUNC_NAME = ".AO_AI_Waveform_Write_Read_Test()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        dev_name = 'Dev2'

        # Configure the Analog Output
        ao_task = nidaqmx.Task()
        ao_chn_str = dev_name + '/ao0'
        ao_task.ao_channels.add_ao_voltage_chan(ao_chn_str, min_val = -10, max_val = +10)
        ao_SR, ao_no_ch = Extract_Sample_Rate(ao_chn_str, dev_name)
        ao_task.timing.cfg_samp_clk_timing(rate = ao_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, 
                                           samps_per_chan = ao_SR, active_edge = nidaqmx.constants.Edge.RISING)

        nu = 3 # frequency in units of Hz
        two_pi_nu = 2.0 * math.pi * nu
        amp = 1.0 # wave amplitude
        phase = 0.0
        t0 = 0.0
        timeInt, w_vals = Generate_Sine_Waveform(ao_SR, ao_SR, t0, nu, amp, phase)

        # https://nitypes.readthedocs.io/en/latest/autoapi/nitypes/waveform/index.html
        # https://nitypes.readthedocs.io/en/latest/autoapi/nitypes/waveform/Timing.html
        waveform = nitypes.waveform.AnalogWaveform(sample_count = ao_SR, 
                                                   timing = nitypes.waveform.Timing.create_with_regular_interval(
                                                       datetime.timedelta(seconds = timeInt.delta) 
                                                       ) 
                                                   )
        #waveform.raw_data[:] = w_vals
        waveform = waveform.from_array_1d(w_vals)
        waveform.units = "Volts"

        # Write the waveform
        
        number_of_samples_written = ao_task.write(waveform, auto_start=True)
        print(f"Generating {number_of_samples_written} voltage samples.")
        ao_task.wait_until_done()
        ao_task.stop()

        # Configure Analog Input
        ai_task = nidaqmx.Task()        
        ai_chn_str = dev_name + '/ai0'
        ai_SR, ai_no_ch = Extract_Sample_Rate(ai_chn_str, dev_name)
        ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, 
                                                min_val = -10, max_val = +10)
        ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, 
                                           samps_per_chan = ai_SR, active_edge = nidaqmx.constants.Edge.RISING)
        
        # Read the waveform
        ai_task.start()
        data = ai_task.read(nidaqmx.constants.READ_ALL_AVAILABLE)
        #data=ai_task.read_waveform()
        ai_task.stop()        

        #print("N_samples read:",len(data))

        print(f"Acquired data: {data.scaled_data}")
        print(f"Channel name: {data.channel_name}")
        print(f"Units: {data.units}")
        print(f"t0: {data.timing.start_time}")
        print(f"dt: {data.timing.sample_interval}")

        # close all tasks
        ao_task.close()
        ai_task.close()

        # Make a plot of the data that has been read
        # t_vals, dT_AO = numpy.linspace(timeInt.start, timeInt.stop, ai_SR, endpoint = True, retstep = True)

        # args = Plotting.plot_arg_single()

        # args.loud = True
        # args.x_label = 'Time (s)'
        # args.y_label = 'Sine Wave'
        # args.marker = Plotting.labs_lins[3]
        # #args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}

        # Plotting.plot_single_curve(t_vals, data, args)

    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AO_Waveform_Write_Test():

     with nidaqmx.Task() as task:
        sampling_rate = 1000.0
        number_of_samples = 1000
        task.ao_channels.add_ao_voltage_chan("Dev2/ao0", min_val = -10, max_val = +10)
        #task.timing.cfg_samp_clk_timing(sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        task.timing.cfg_samp_clk_timing(rate = sampling_rate, sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS, 
                                           samps_per_chan = number_of_samples, active_edge = nidaqmx.constants.Edge.RISING)

        actual_sampling_rate = task.timing.samp_clk_rate
        print(f"Actual sampling rate: {actual_sampling_rate:g} S/s")

        nu = 10 # frequency in units of Hz
        two_pi_nu = 2.0 * math.pi * nu
        amp = 5.0 # wave amplitude
        phase = 0.0
        t0 = 0.0
        timeInt, data = Generate_Sine_Waveform(sampling_rate, number_of_samples, t0, nu, amp, phase)
        
        task.write(data)
        task.start()

        input("Generating voltage continuously. Press Enter to stop.\n")

        task.stop()

        #task.close()

    # with nidaqmx.Task() as task:
    #     total_samples = 1000
    #     task.ao_channels.add_ao_voltage_chan("Dev2/ao0")
    #     task.timing.cfg_samp_clk_timing(1000.0, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=total_samples)

    #     waveform = nitypes.waveform.AnalogWaveform(sample_count=total_samples)
    #     waveform.raw_data[:] = [5.0 * i / total_samples for i in range(total_samples)]
    #     waveform.units = "Volts"

    #     number_of_samples_written = task.write(waveform, auto_start=True)
    #     print(f"Generating {number_of_samples_written} voltage samples.")
    #     task.wait_until_done()
    #     task.stop()

def AI_Waveform_Read_Test():

    # This seems to work well enough

    with nidaqmx.Task() as task:
        SR = AI_SR_MAX
        dT = 1.0 / float(SR)
        n_samples = AI_SR_MAX
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        task.timing.cfg_samp_clk_timing(rate = SR, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=n_samples)

        waveform = task.read(nidaqmx.constants.READ_ALL_AVAILABLE)
        t0 = 0.0
        tf = t0 + n_samples * dT
        times = numpy.arange(t0, tf, dT)
        
        plot.plot(times, waveform)
        # plot.xlabel("Seconds")
        # plot.ylabel(waveform.units)
        # plot.title(waveform.channel_name)
        plot.grid(True)

        plot.show()

        task.stop()

# Actual routines that you would want with a DAQ

def Generate_Sine_Waveform(sample_rate, no_smpls, t_start = 0.0, frequency = 1.0, amplitude = 1.0, phase = 0.0):
    """
    Generate a sine waveform

    Inputs
    sample_rate(int) and no_smpls(int) to be determined by NI-DAQ AO
    t_start(float) time at which sine wave must start in units of second
    frequency(float) in units of Hz
    amplitude(float) in units of volt in range [-10, 10]
    phase(float) is dimensionless

    Output is a tuple with the following items
    timeInterval(SweepSpace object) that contains the data needed to generate time samples using numpy.linspace
    w_vals(float numpy array) contains sine waveform values

    R. Sheehan 4 - 12 - 2025
    """
    
    FUNC_NAME = ".Generate_Sine_Waveform()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        c1 = True if sample_rate > 0 else False
        c2 = True if no_smpls > 0 else False
        c3 = True if frequency > 0 else False
        c4 = True if math.fabs(amplitude) <= 10 else False
        c10 = c1 and c2 and c3 and c4

        if c10:
            deltaT = ( 1.0 / float(sample_rate) )
            t0 = t_start
            two_pi_nu = 2.0 * math.pi * frequency
            t_vals = numpy.array([]) # instantiate an empty numpy array
            w_vals = numpy.array([]) # instantiate an empty numpy array
            count = 0
            while count < no_smpls:
                sval = amplitude * math.sin(two_pi_nu * t0 + phase)
                w_vals = numpy.append(w_vals, sval )
                t0 += deltaT
                count += 1

            # instantiate a SweepSpace object to enable time samples to be generated later using 
            # numpy.linspace(timeInterval.start, timeInterval.stop, timeInterval.Nsteps, endpoint=True, retstep=True)
            timeInterval = Sweep_Interval.SweepSpace(no_smpls, t_start, t0)
            
            return (timeInterval, w_vals)
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nsample_rate is negative'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nno_smpls is negative'
            if c3 is False: ERR_STATEMENT = ERR_STATEMENT + '\nfrequency is negative'
            if c4 is False: ERR_STATEMENT = ERR_STATEMENT + '\namplitude is out of range for NI-DAQ'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def Generate_Square_Waveform(sample_rate, no_smpls, t_start = 0.0, frequency = 1.0, amplitude = 1.0, phase = 0.0, pulsed = False):
    """
    Generate a square waveform

    Inputs
    sample_rate(int) and no_smpls(int) to be determined by NI-DAQ AO
    t_start(float) time at which square wave must start in units of second
    frequency(float) in units of Hz
    amplitude(float) in units of volt in range [-10, 10]
    phase(float) is dimensionless
    pulsed(boolean) decides whether or not to output non-negative pulses

    Output is a tuple with the following items
    timeInterval(SweepSpace object) that contains the data needed to generate time samples using numpy.linspace
    w_vals(float numpy array) contains square waveform values

    R. Sheehan 4 - 12 - 2025
    """

    # notes on square waves
    # https://en.wikipedia.org/wiki/Square_wave_(waveform)
    # https://mathworld.wolfram.com/SquareWave.html
    
    FUNC_NAME = ".Generate_Square_Waveform()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        c1 = True if sample_rate > 0 else False
        c2 = True if no_smpls > 0 else False
        c3 = True if frequency > 0 else False
        c4 = True if math.fabs(amplitude) <= 10 else False
        c10 = c1 and c2 and c3 and c4

        if c10:
            deltaT = ( 1.0 / float(sample_rate) )
            t0 = t_start
            two_pi_nu = 2.0 * math.pi * frequency
            t_vals = numpy.array([]) # instantiate an empty numpy array
            w_vals = numpy.array([]) # instantiate an empty numpy array
            count = 0
            while count < no_smpls:
                sval = math.sin(two_pi_nu * t0 + phase)
                # python does not have a built-in signum function, but it does have copysign which can be used
                # copysign(x,y): Return x with the sign of y
                val = math.copysign(amplitude, sval) # sq wave = signum (sine wave)
                if pulsed:
                    w_vals = numpy.append(w_vals, val if val > 0.0 else 0.0 ) # only want positive portion of sq wave
                else:
                    w_vals = numpy.append(w_vals, val)
                t0 += deltaT
                count += 1

            # instantiate a SweepSpace object to enable time samples to be generated later using 
            # numpy.linspace(timeInterval.start, timeInterval.stop, timeInterval.Nsteps, endpoint=True, retstep=True)
            timeInterval = Sweep_Interval.SweepSpace(no_smpls, t_start, t0)
            
            return (timeInterval, w_vals)
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nsample_rate is negative'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nno_smpls is negative'
            if c3 is False: ERR_STATEMENT = ERR_STATEMENT + '\nfrequency is negative'
            if c4 is False: ERR_STATEMENT = ERR_STATEMENT + '\namplitude is out of range for NI-DAQ'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def Generate_Triangle_Waveform(sample_rate, no_smpls, t_start = 0.0, frequency = 1.0, amplitude = 1.0, phase = 0.0, pulsed = False):
    """
    Generate a triangle waveform

    Inputs
    sample_rate(int) and no_smpls(int) to be determined by NI-DAQ AO
    t_start(float) time at which triangle wave must start in units of second
    frequency(float) in units of Hz
    amplitude(float) in units of volt in range [-10, 10]
    phase(float) is dimensionless
    pulsed(boolean) decides whether or not to output non-negative pulses

    Output is a tuple with the following items
    timeInterval(SweepSpace object) that contains the data needed to generate time samples using numpy.linspace
    w_vals(float numpy array) contains triangle waveform values

    R. Sheehan 4 - 12 - 2025
    """

    # notes on triangular wave
    # https://en.wikipedia.org/wiki/Triangle_wave
    # https://mathworld.wolfram.com/TriangleWave.html
    
    FUNC_NAME = ".Generate_Pulse_Waveform()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        c1 = True if sample_rate > 0 else False
        c2 = True if no_smpls > 0 else False
        c3 = True if frequency > 0 else False
        c4 = True if math.fabs(amplitude) <= 10 else False
        c10 = c1 and c2 and c3 and c4

        if c10:
            deltaT = ( 1.0 / float(sample_rate) )
            t0 = t_start
            two_pi_nu = 2.0 * math.pi * frequency
            amp = (2.0 * amplitude) / math.pi
            t_vals = numpy.array([]) # instantiate an empty numpy array
            w_vals = numpy.array([]) # instantiate an empty numpy array
            count = 0
            while count < no_smpls:
                sval = math.sin(two_pi_nu * t0 + phase)
                val = amp * math.asin( sval )
                if pulsed:
                    w_vals = numpy.append(w_vals, math.fabs(val) ) # convert to triangular pulses by taking math.fabs(val)
                else:
                    w_vals = numpy.append(w_vals, val )
                t0 += deltaT
                count += 1

            # instantiate a SweepSpace object to enable time samples to be generated later using 
            # numpy.linspace(timeInterval.start, timeInterval.stop, timeInterval.Nsteps, endpoint=True, retstep=True)
            timeInterval = Sweep_Interval.SweepSpace(no_smpls, t_start, t0)
            
            return (timeInterval, w_vals)
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nsample_rate is negative'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nno_smpls is negative'
            if c3 is False: ERR_STATEMENT = ERR_STATEMENT + '\nfrequency is negative'
            if c4 is False: ERR_STATEMENT = ERR_STATEMENT + '\namplitude is out of range for NI-DAQ'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def Extract_Sample_Rate(physical_channel_str, device_name, loud = False):
    """
    Extract the AI / AO sample rate based on the data contained in the physical_channel string descriptor
    Always want to set sample rate to be at its maximum
    
    Methods aims to process physical_channel string descriptors of the form
    'device_name/a<x><v1>', single channel operation
    'device_name/a<x><v1>:<v2>', multiple sequential channel operation
    'device_name/axv1, device_name/axv2, ..., device_name/axvn', multiple channel operation
    'device_name/a<x><v1>:<v2>, device_name/axv3, ..., device_name/axvn', multiple channel operation
    'device_name/a<x><v1>:<v2>, device_name/a<x><v3>:<v4>', multiple channel operation
    
    <x> = i or o
    <v1>, <v2> indicate the sequential channel numbers on the DAQ
    
    If a user inputs physical_channel_str with mix of ao and ai channels an exception will be thrown by nidaqmx
    
    R. Sheehan 27 - 11 - 2025
    """

    FUNC_NAME = ".Extract_Sample_Rate()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        c1 = True if physical_channel_str != '' else False
        c2 = True if device_name != '' else False
        c10 = c1 and c2

        if c10:
            SR_MAX = AI_SR_MAX if 'i' in physical_channel_str else AO_SR_MAX
            
            reduced_str = physical_channel_str.replace( device_name+'/', '' ) # strip out the device_name from the physical_channel_str
            if loud: print("Physical Channels: ",reduced_str)

            if ',' in physical_channel_str and ':' not in physical_channel_str:
                # physical_channel_str is of the form 'device_name/axv1, device_name/axv2, ..., device_name/axvn'
                ch_nums = list ( set ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", reduced_str ) ) ) ) # set removes duplicates from the list if they exist
                no_ch = len(ch_nums)
                SR = int(SR_MAX / no_ch)
            elif ':' in physical_channel_str and ',' not in physical_channel_str:
                # physical_channel_str is of the form 'device_name/axv1:v2'
                # <x> = i or o
                # <v1>, <v2> indicate the sequential channel numbers on the DAQ
                ch_nums = list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", reduced_str ) ) )
                no_ch = 1 + ( max(ch_nums) - min(ch_nums) ) # use this in case v1 != 0
                SR = int(SR_MAX / no_ch)
            elif ':' in physical_channel_str and ',' in physical_channel_str:
                # physical_channel_str is of the form 'device_name/a<x><v1>:<v2>, device_name/axv3, ..., device_name/axvn'
                # physical_channel_str is of the form 'device_name/a<x><v1>:<v2>, device_name/a<x><v3>:<v4>'
                # <x> = i or o
                # <v1>, ..., <vn> indicate the channel numbers on the DAQ, not necessarily sequential
                ch_nums = []
                for item in reduced_str.split(','):
                    if ":" in item:
                        nums = list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", item) ) )
                        ch_nums.extend( range( nums[0], 1+nums[1], 1 ) )
                    else:
                        ch_nums.extend(list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", item) ) ) )
                ch_nums = list( set( ch_nums ) ) # set removes duplicates from the list if they exist
                no_ch = len(ch_nums)
                SR = SR_MAX / no_ch
            else:
                # physical_channel_str is of the form 'device_name/a<x><v1>'
                # indicating a single channel is being used
                # <x> = i or o
                # <v1> indicates the channel number on the DAQ
                ch_nums = list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", reduced_str ) ) )
                no_ch = 1
                SR = SR_MAX

            if loud: 
                print("Channels:", ch_nums)
                print("No. Channels:",no_ch)
                print("Sample Rate:", SR)
                print()

            return [SR, no_ch]
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in physical_channel_str'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in device_name'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AI_Monitor(physical_channel_str = 'Dev2/ai0:3', device_name = 'Dev2', loud = False):
    """
    Use NI-DAQ to measure multiple real-time AI

    differential read is assumed on all channels

    R. Sheehan 3 - 12 - 2025
    """

    FUNC_NAME = ".AI_Monitor()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        c1 = True if physical_channel_str != '' else False
        c2 = True if device_name != '' else False
        c10 = c1 and c2

        if c10:
            # Extract the sample rate per channel
            ai_chn_str = physical_channel_str

            ai_SR, ai_no_ch = Extract_Sample_Rate(ai_chn_str, device_name)

            # Configure Analog Input
            ai_task = nidaqmx.Task()        

            # If ai_chn_str is not correctly defined an exception will be thrown by nidaqmx
            ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, 
                                                    min_val = -10, max_val = +10)
            
            # Configure the sampling timing
            # Note that when reading data later no. samples to be read must equal samps_per_chan as defined
            # Otherwise an exception will be thrown by nidaqmx
            ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, 
                                               samps_per_chan = ai_SR>>1, active_edge = nidaqmx.constants.Edge.RISING)

            # AI Channel Monitoring


            # Close off the ai_task
            ai_task.close()
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in physical_channel_str'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in device_name'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

