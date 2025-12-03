
# Import various modules

from ast import Try, TryStar
import os
from pickle import FALSE
import NI_DAQ_Lib

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

def main():
    pass

if __name__ == '__main__':
    main()

    pwd = os.getcwd() # get current working directory

    print(pwd)
    
    #NI_DAQ_Lib.AO_Write_Test()
    
    NI_DAQ_Lib.AI_Read_Test()
    
    #NI_DAQ_Lib.AO_AI_Loopback_Test()

    #NI_DAQ_Lib.AI_Read_Multiple_Channels()

    #NI_DAQ_Lib.NI_DAQ_String_Hacking()

    #NI_DAQ_Lib.NI_DAQ_SR_Extract_Testing()

    #NI_DAQ_Lib.AI_Read_Multiple_Channels_with_Clock()

    #NI_DAQ_Lib.DC_Sweep_Diode()