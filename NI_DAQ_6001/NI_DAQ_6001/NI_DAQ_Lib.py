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

MOD_NAME_STR = "NI_DAQ_Lib"
AI_SR_MAX = 20000 # max sample rate on single AI channel, units of Hz
AO_SR_MAX = 5000 # max sample rate on single AO channel, units of Hz

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
                                               samps_per_chan = ai_SR, active_edge = nidaqmx.constants.Edge.RISING)

            # AI Channel Monitoring
            DELAY = 10
            N_meas = 7
            count = 0
            while count < N_meas:

                count += 1

            # Close off the ai_task
            ai_task.close()
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in physical_channel_str'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in device_name'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)

def AI_Timed_Measurement(physical_channel_str = 'Dev2/ai0:3', device_name = 'Dev2', total_time = 10, no_meas = 10, loud = False):
    """
    Use NI-DAQ to measure multiple AI for specified time period, with delay between measurements

    differential read is assumed on all channels

    R. Sheehan 27 - 1 - 2026
    """

    FUNC_NAME = ".AI_Monitor()" # use this in exception handling messages
    ERR_STATEMENT = "Error: " + MOD_NAME_STR + FUNC_NAME

    try:
        c1 = True if physical_channel_str != '' else False
        c2 = True if device_name != '' else False
        c3 = True if total_time > 0 else False
        c3 = True if no_meas > 3 else False
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
                                               samps_per_chan = ai_SR, active_edge = nidaqmx.constants.Edge.RISING)

            # AI Channel Monitoring
            DELAY = (60 * total_time) / no_meas # compute delay time in seconds
            if loud:
                print("No. Measurement Channels = ",ai_no_ch)
                print("AI Sample Rate = ",ai_SR/1000,"( kHz )")                
                print("Delay Time = ",DELAY," ( s )")
            count = 0
            while count < no_meas:
                time.sleep(DELAY)
                # read some data
                # documentation for read https://nidaqmx-python.readthedocs.io/en/stable/task.html#nidaqmx.task.InStream.read
                data = ai_task.read(nidaqmx.constants.READ_ALL_AVAILABLE)

                if ai_no_ch > 1:
                    for i in range(0, ai_no_ch, 1):
                        avg = numpy.mean(data[i])
                        stdev = numpy.std(data[i], ddof = 1)
                        print("ai%(v1)d: %(v2)0.4f +/- %(v3)0.4f (V)"%{"v1":i, "v2":avg, "v3":stdev})
                    print()
                else:
                    avg = numpy.mean(data)
                    stdev = numpy.std(data, ddof = 1)
                    print("ai%(v1)d: %(v2)0.4f +/- %(v3)0.4f (V)"%{"v1":0, "v2":avg, "v3":stdev})

                count += 1

            # It is possible to compute the total average by combining the averages from each of the individual measurements, similarly for standard deviation
            # https://stats.stackexchange.com/questions/55999/is-it-possible-to-find-the-combined-standard-deviation?noredirect=1&lq=1
            # https://stats.stackexchange.com/questions/43031/how-to-prove-that-averaging-averages-of-different-partitions-of-a-dataset-produc
            # https://stats.stackexchange.com/questions/10441/how-to-calculate-the-variance-of-a-partition-of-variables?noredirect=1&lq=1
            # This means that for a long measurement with a very large no. of samples the raw data need not be stored in memory
            # Best practice is probably to write the raw data to a file as it's being measured
            # Then measurement distributions, taken under different conditions, can be compared. 

            # Close off the ai_task
            ai_task.close()
        else:
            if c1 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in physical_channel_str'
            if c2 is False: ERR_STATEMENT = ERR_STATEMENT + '\nNo data contained in device_name'
            raise Exception
    except Exception as e:
        print(ERR_STATEMENT)
        print(e)