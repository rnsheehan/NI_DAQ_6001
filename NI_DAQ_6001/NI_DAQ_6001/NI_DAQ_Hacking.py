"""
Hacking around with the NI-DAQ to figure out how it works

R. Sheehan 21 - 11 - 2025
"""

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
import NI_DAQ_Lib

MOD_NAME_STR = "NI_DAQ_Hacking"
AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

# Basic Test and Operation Routines
# Use these to check basic DAQ communication and functionality

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
    # ai_chn_str = 'Dev2/ai1:3, Dev2/ai4, Dev2/ai6'
    # ai_chn_str = 'Dev2/ai0:1, Dev2/ai5:7'
    # Need to count the number of channels being accessed

    AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
    AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

    # No commas, single semi-colon
    ai_chn_str = 'Dev2/ai0:2'
    #ai_chn_str = 'Dev2/ai3:6'
    print()
    print(ai_chn_str)
    #print(int(ai_chn_str.split(':')[-1]))    
    #print(ai_chn_str.replace('Dev2/',''))
    #print( re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) )
    #print( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) 
    #print( max ( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) )
    ch_nums = list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) )
    no_ch = 1 + ( max(ch_nums) - min(ch_nums) ) # use this in case min val != 0
    smpl_rt = AI_SR_MAX / no_ch
    print("Channel Numbers: ", ch_nums)
    print("No. channels: ", no_ch )
    print("Sample Rate per channel: ", smpl_rt )

    # No semi-colons, multiple commas
    ai_chn_str = 'Dev2/ai0, Dev2/ai1, Dev2/ai4, Dev2/ai7, Dev2/ai1'
    print()
    print(ai_chn_str)
    #print(ai_chn_str.replace('Dev2/',''))
    #print( re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) )
    #print( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) 
    #print( len ( list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) )
    ch_nums = list ( set( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", ai_chn_str.replace( 'Dev2/', '' ) ) ) ) ) # set removes duplicates from the list if they exist
    no_ch = len(ch_nums)
    smpl_rt = AI_SR_MAX / no_ch
    print("Channel Numbers: ", ch_nums)
    print("No. channels: ", no_ch )
    print("Sample Rate per channel: ", smpl_rt )

    # This works but how do you handle general cases like the one below? 
    # mix semi-colon, commas

    # re.findall(r"[-+]?\d+[\.]?\d*", the_string)

    ai_chn_str = 'Dev2/ai1:3, Dev2/ai4, Dev2/ai6, Dev2/ai6'
    print()
    print(ai_chn_str)
    print(ai_chn_str.replace('Dev2/','').split(','))
    ch_nums = []
    for item in ai_chn_str.replace('Dev2/','').split(','):
        if ":" in item:
            nums = list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", item) ) )
            ch_nums.extend( range( nums[0], 1+nums[1], 1 ) )
        else:
            ch_nums.extend(list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", item) ) ) )
    ch_nums = list( set( ch_nums ) )
    no_ch = len(ch_nums)
    smpl_rt = AI_SR_MAX / no_ch
    print("Channel Numbers: ", ch_nums)
    print("No. channels: ", no_ch )
    print("Sample Rate per channel: ", smpl_rt )

    ai_chn_str = 'Dev2/ai0:1, Dev2/ai5:7'
    print()
    print(ai_chn_str)
    print(ai_chn_str.replace('Dev2/','').split(','))
    ch_nums = []
    for item in ai_chn_str.replace('Dev2/','').split(','):
        if ":" in item:
            nums = list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", item) ) )
            ch_nums.extend( range( nums[0], 1+nums[1], 1 ) )
        else:
            ch_nums.extend(list ( map ( int, re.findall(r"[-+]?\d+[\.]?\d*", item) ) ))
    no_ch = len(ch_nums)
    smpl_rt = AI_SR_MAX / no_ch
    print("Channel Numbers: ", ch_nums)
    print("No. channels: ", no_ch )
    print("Sample Rate per channel: ", smpl_rt )

def NI_DAQ_SR_Extract_Testing():

    # Test the method for computing the SR based on the physical_descriptor str

    #ai_chn_str = 'Dev2/ai0:2'
    ai_chn_str = 'Dev2/ai3:6'
    NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, 'Dev2', True)

    ai_chn_str = 'Dev2/ai0, Dev2/ai1, Dev2/ai4, Dev2/ai7, Dev2/ai1'
    NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, 'Dev2', True)

    ai_chn_str = 'Dev2/ai1:3, Dev2/ai4, Dev2/ai6, Dev2/ai6'
    NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, 'Dev2', True)

    ai_chn_str = 'Dev2/ai0:1, Dev2/ai5:7'
    NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, 'Dev2', True)

    ao_chn_str = 'Dev2/ao0:1'
    NI_DAQ_Lib.Extract_Sample_Rate(ao_chn_str, 'Dev2', True)

def Making_Waves():

    # Ensure that you can make some waves with specific frequencies and sample rates
    # R. Sheehan 4 - 12 -  2025

    AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
    AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz
    dT_AO = 1.0 / AO_SR_MAX

    PLOT_SINE_WAVE = False
    if PLOT_SINE_WAVE:
        
        nu = 3 # frequency in units of Hz
        two_pi_nu = 2.0 * math.pi * nu
        amp = 1.0 # wave amplitude
        phase = 0.0
        t0 = 0.0

        timeInt, w_vals = NI_DAQ_Lib.Generate_Sine_Waveform(AO_SR_MAX, AO_SR_MAX, t0, nu, amp, phase)
        t_vals, dT_AO = numpy.linspace(timeInt.start, timeInt.stop, timeInt.Nsteps, endpoint = True, retstep = True)

        # generate a plot
        args = Plotting.plot_arg_single()

        args.loud = True
        args.x_label = 'Time (s)'
        args.y_label = 'Sine Wave'
        args.marker = Plotting.labs_lins[3]
        args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}

        Plotting.plot_single_curve(t_vals, w_vals, args)

    PLOT_SQUARE_WAVE = False
    if PLOT_SQUARE_WAVE:
        
        nu = 3 # frequency in units of Hz
        n_smpls = AI_SR_MAX # no. of samples
        two_pi_nu = 2.0 * math.pi * nu
        amp = 1.0 # wave amplitude
        phase = 0.0 # phase offset
        t0 = 0.0

        timeInt, ww_vals = NI_DAQ_Lib.Generate_Sine_Waveform(AO_SR_MAX, AO_SR_MAX, t0, nu, amp, phase)
        timeInt, w_vals = NI_DAQ_Lib.Generate_Square_Waveform(AO_SR_MAX, AO_SR_MAX, t0, nu, amp, phase)
        t_vals, dT_AO = numpy.linspace(timeInt.start, timeInt.stop, timeInt.Nsteps, endpoint = True, retstep = True)

        # generate a plot
        # args = Plotting.plot_arg_single()

        # args.loud = True
        # args.x_label = 'Time (s)'
        # args.y_label = 'Square Wave'
        # args.marker = Plotting.labs_lins[3]
        # args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}

        # Plotting.plot_single_curve(t_vals, w_vals, args)

        args = Plotting.plot_arg_multiple()

        args.loud = True
        args.x_label = 'Time (s)'
        args.y_label = 'Square Wave'
        args.crv_lab_list = ['Square', 'Sine']
        args.mrk_list = [Plotting.labs_lins[3], Plotting.labs_lins[4]]
        args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}
        
        Plotting.plot_multiple_curves([[t_vals, w_vals], [t_vals, ww_vals]], args)

    PLOT_PULSE_WAVE = False
    if PLOT_PULSE_WAVE:
        
        nu = 3 # frequency in units of Hz
        n_smpls = AI_SR_MAX # no. of samples
        two_pi_nu = 2.0 * math.pi * nu
        amp = 1.0 # wave amplitude
        phase = 0.0 # phase offset
        t0 = 0.0

        timeInt, ww_vals = NI_DAQ_Lib.Generate_Sine_Waveform(AO_SR_MAX, AO_SR_MAX, t0, nu, amp, phase)
        timeInt, w_vals = NI_DAQ_Lib.Generate_Square_Waveform(AO_SR_MAX, AO_SR_MAX, t0, nu, amp, phase, pulsed = True)
        t_vals, dT_AO = numpy.linspace(timeInt.start, timeInt.stop, timeInt.Nsteps, endpoint = True, retstep = True)

        # generate a plot
        # args = Plotting.plot_arg_single()

        # args.loud = True
        # args.x_label = 'Time (s)'
        # args.y_label = 'Pulse Wave'
        # args.marker = Plotting.labs_lins[3]
        # args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}

        # Plotting.plot_single_curve(t_vals, w_vals, args)

        args = Plotting.plot_arg_multiple()

        args.loud = True
        args.x_label = 'Time (s)'
        args.y_label = 'Pulse Wave'
        args.crv_lab_list = ['Pulse', 'Sine']
        args.mrk_list = [Plotting.labs_lins[3], Plotting.labs_lins[4]]
        args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}
        
        Plotting.plot_multiple_curves([[t_vals, w_vals], [t_vals, ww_vals]], args)

    PLOT_TRIANGLE_WAVE = False
    if PLOT_TRIANGLE_WAVE:
        nu = 3 # frequency in units of Hz
        amp = 1.0 # wave amplitude
        phase = 0.0 # phase offset
        t0 = 0.0

        timeInt, ww_vals = NI_DAQ_Lib.Generate_Sine_Waveform(AO_SR_MAX>>1, AO_SR_MAX>>1, t0, nu, amp, phase)
        timeInt, w_vals = NI_DAQ_Lib.Generate_Triangle_Waveform(AO_SR_MAX>>1, AO_SR_MAX>>1, t0, nu, amp, phase, pulsed = True)
        t_vals, dT_AO = numpy.linspace(timeInt.start, timeInt.stop, timeInt.Nsteps, endpoint = True, retstep = True)

        # generate a plot
        # args = Plotting.plot_arg_single()

        # args.loud = True
        # args.x_label = 'Time (s)'
        # args.y_label = 'Pulse Wave'
        # args.marker = Plotting.labs_lins[3]
        # args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}

        # Plotting.plot_single_curve(t_vals, w_vals, args)

        args = Plotting.plot_arg_multiple()

        args.loud = True
        args.x_label = 'Time (s)'
        args.y_label = 'Triangle Wave'
        args.crv_lab_list = ['Triangle', 'Sine']
        args.mrk_list = [Plotting.labs_lins[3], Plotting.labs_lins[4]]
        args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}
        
        Plotting.plot_multiple_curves([[t_vals, w_vals], [t_vals, ww_vals]], args)    

    PLOT_RANDOM_WAVE = True
    if PLOT_RANDOM_WAVE:
        
        amp = 1.0 # wave amplitude
        t0 = 0.0
        tpulse = 100 # pulse width in milliseconds

        timeInt, w_vals = NI_DAQ_Lib.Generate_Random_Pulse_Waveform(AO_SR_MAX, 5 * AO_SR_MAX, t0, amp, tpulse / 1000.0)
        t_vals, dT_AO = numpy.linspace(timeInt.start, timeInt.stop, timeInt.Nsteps, endpoint = True, retstep = True)

        # generate a plot
        args = Plotting.plot_arg_single()

        args.loud = True
        args.x_label = 'Time (s)'
        args.y_label = 'Random Pulse Train'
        args.marker = Plotting.labs_lins[3]
        args.plt_title = r'N$_{smpls}$ = %(v1)d, $\delta$t = %(v2)0.3f (ms)'%{"v1":len(t_vals), "v2":1000.0*dT_AO}

        Plotting.plot_single_curve(t_vals, w_vals, args)

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
        ao_SR, ao_no_ch = NI_DAQ_Lib.Extract_Sample_Rate(ao_chn_str, dev_name)
        
        # Configure Analog Input
        ai_task = nidaqmx.Task()        
        ai_chn_str = 'Dev1/ai0:2'
        ai_SR, ai_no_ch = NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, dev_name, True)
        ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, min_val = -10, max_val = +10)
        ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan = ai_SR, active_edge = nidaqmx.constants.Edge.RISING)
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

        print("ai SR = ",ai_SR,' Hz => dT = ',1000.0 / float(ai_SR),' ( ms )')
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
        ao_SR, ao_no_ch = NI_DAQ_Lib.Extract_Sample_Rate(ao_chn_str, dev_name)
        ao_task.timing.cfg_samp_clk_timing(rate = ao_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, 
                                           samps_per_chan = ao_SR, active_edge = nidaqmx.constants.Edge.RISING)

        nu = 3 # frequency in units of Hz
        two_pi_nu = 2.0 * math.pi * nu
        amp = 1.0 # wave amplitude
        phase = 0.0
        t0 = 0.0
        timeInt, w_vals = NI_DAQ_Lib.Generate_Sine_Waveform(ao_SR, ao_SR, t0, nu, amp, phase)

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
        ai_SR, ai_no_ch = NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, dev_name)
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

    # Use the analog output to write a waveform to the output stream

    # Configure the analog output to write continuously
    ao_chn_str = "Dev2/ao0"
    ao_SR, _ = NI_DAQ_Lib.Extract_Sample_Rate(ao_chn_str, 'Dev2')
    number_of_samples = ao_SR

    ao_task = nidaqmx.Task()
    ao_task.ao_channels.add_ao_voltage_chan(ao_chn_str, min_val = -10, max_val = +10)
    ao_task.timing.cfg_samp_clk_timing(rate = ao_SR, sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS, 
                                       samps_per_chan = number_of_samples, active_edge = nidaqmx.constants.Edge.RISING)

    actual_sampling_rate = ao_task.timing.samp_clk_rate # read the actual sample rate
    print(f"Actual sampling rate: {actual_sampling_rate:g} S/s")

    # Generate the waveform data
    nu = 10 # frequency in units of Hz
    two_pi_nu = 2.0 * math.pi * nu
    amp = math.sqrt(2) # wave amplitude
    phase = 0.0
    t0 = 0.0
    #timeInt, data = NI_DAQ_Lib.Generate_Sine_Waveform(ao_SR, number_of_samples, t0, nu, amp, phase)
    #timeInt, data = NI_DAQ_Lib.Generate_Triangle_Waveform(ao_SR, number_of_samples, t0, nu, amp, phase, pulsed = True)
    timeInt, data = NI_DAQ_Lib.Generate_Square_Waveform(ao_SR, number_of_samples, t0, nu, amp, phase, pulsed = False)

    # Configure the analog input
    ai_chn_str = "Dev2/ai3"
    ai_SR, _ = NI_DAQ_Lib.Extract_Sample_Rate(ai_chn_str, 'Dev2')
    number_of_samples = ai_SR

    # Configure Analog Input
    ai_task = nidaqmx.Task()        

    # If ai_chn_str is not correctly defined an exception will be thrown by nidaqmx
    ai_task.ai_channels.add_ai_voltage_chan(ai_chn_str, terminal_config = nidaqmx.constants.TerminalConfiguration.DIFF, 
                                            min_val = -10, max_val = +10)
            
    # Configure the sampling timing
    # Note that when reading data later no. samples to be read must equal samps_per_chan as defined
    # Otherwise an exception will be thrown by nidaqmx
    ai_task.timing.cfg_samp_clk_timing(ai_SR, sample_mode = nidaqmx.constants.AcquisitionType.FINITE, 
                                        samps_per_chan = number_of_samples, active_edge = nidaqmx.constants.Edge.RISING)
    
    # Write the waveform data until you want to stop
    ao_task.write(data)
    ao_task.start()

    count = 0
    while count < 5:
        # Read the waveform data into memory
        ai_task.start()
        waveform = ai_task.read(nidaqmx.constants.READ_ALL_AVAILABLE)

        t0 = time.time()
        dT = 1.0 / float(ai_SR)
        tf = t0 + number_of_samples * dT
        times = numpy.arange(t0, tf, dT)
        
        plot.plot(times, waveform)
        # plot.xlabel("Seconds")
        # plot.ylabel(waveform.units)
        # plot.title(waveform.channel_name)
        plot.grid(True)
        plot.show()

        ai_task.stop()

        count += 1

    input("Generating voltage continuously. Press Enter to stop.\n")

    ao_task.stop()

    ao_task.close()

    ai_task.close()

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