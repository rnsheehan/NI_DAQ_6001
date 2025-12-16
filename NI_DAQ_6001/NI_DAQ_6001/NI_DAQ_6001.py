
# Import various modules

from ast import Try, TryStar
import os
from pickle import FALSE
import math
import numpy
import NI_DAQ_Lib
import Plotting

# The aim of this script is to establish comms with NI-DAQ USB 6001
# Official Documentation: https://nidaqmx-python.readthedocs.io/en/stable/
# Examples with explanation: https://nidaqmx-python.readthedocs.io/en/stable/#python-examples
# Nice introduction: https://www.halvorsen.blog/documents/programming/python/resources/powerpoints/DAQ%20with%20Python.pdf
# Examples online: https://github.com/ni/nidaqmx-python/tree/master
# R. Sheehan 21 - 11 - 2025

MOD_NAME_STR = "NI_DAQ_600x"

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

    PLOT_PULSE_WAVE = True
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

def main():
    pass

if __name__ == '__main__':
    main()

    pwd = os.getcwd() # get current working directory

    print(pwd)
    
    #Making_Waves()

    #NI_DAQ_Lib.AO_Write_Test()
    
    #NI_DAQ_Lib.AI_Read_Test()
    
    #NI_DAQ_Lib.AO_AI_Loopback_Test()

    #NI_DAQ_Lib.AI_Read_Multiple_Channels()

    #NI_DAQ_Lib.NI_DAQ_String_Hacking()

    #NI_DAQ_Lib.NI_DAQ_SR_Extract_Testing()

    #NI_DAQ_Lib.AI_Read_Multiple_Channels_with_Clock()

    #NI_DAQ_Lib.DC_Sweep_Diode()

    NI_DAQ_Lib.AO_Waveform_Write_Test()

    #NI_DAQ_Lib.AI_Waveform_Read_Test()