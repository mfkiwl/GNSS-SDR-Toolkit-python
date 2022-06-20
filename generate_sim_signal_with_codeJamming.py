from cmath import pi
from math import exp, floor
from random import sample
from source_processor.file_source_processor import FileSourceThread
import threading
import numpy as np
from queue import Queue
from channel.tracking.track_thread import TrackThread
from public.cal_CA_code import generateCAcode


def generate_sim_sig(filename,
                    total_time,
                    prn,
                    jamming_prn,        #prn of jamming signal
                    carrier_freq,       #carrier frequency 
                    freq_shift,         #frequency shift of jamming signal
                    code_phase_shift,   #code phase shift of jamming signal, in chips
                    sample_rate,        #sample frequency 6MHz
                    JSR                 #jamming to signal ratio, in db
                    ):       
    #generate simple signal
    ## settings 
    fid=open(filename,'wb')
    fid.close()    

    # calculate constants
    code_frequency=1.023e6               #chip per second
    code=generateCAcode(prn)
    jamming_code=generateCAcode(jamming_prn)
    jamming_code=np.roll(jamming_code,code_phase_shift)
    jamming_carrier=carrier_freq+freq_shift
    jamming_A=10**(JSR/20)                          #amplitude of jamming signal

    #initial analyse of jamming to authentic signal
    direct_effect=np.sum(code*jamming_code)*jamming_A
    print("Direct effect: %f"%(direct_effect/1023))

    for i in range(total_time): #s
        fid=open(filename,'ab')
        databit_stream=np.ones([1000,int(sample_rate/1e3)])
        databit=1
        for j in range(0,1000):
            if(j%20==0 and np.random.rand(1)[0]>0.3):
                databit=-1*databit
            databit_stream[j,:]=databit
            
        databit_stream=databit_stream.flatten()
        
        t=np.linspace(0,1,int(sample_rate),False)
        cur_jamming_phase=t*2*pi*jamming_carrier
        cur_carrier_phase=t*2*pi*carrier_freq
        cur_carrier_phase=cur_carrier_phase%(2*pi)
        cur_jamming_phase=cur_jamming_phase%(2*pi)

        cur_code_phase=t*code_frequency
        cur_code_phase=cur_code_phase%1023
        cur_chip_index=np.floor(cur_code_phase).astype('i4')
        cur_jamming_chip_index=cur_chip_index.copy()
        cur_code=code[cur_chip_index]
        cur_jamming_code=jamming_code[cur_jamming_chip_index]
        cur_sig=np.exp(1j*cur_carrier_phase)
        cur_sig=cur_sig*cur_code*databit_stream
        cur_jamming_sig=np.exp(1j*cur_jamming_phase)
        cur_jamming_sig=cur_jamming_sig*cur_jamming_code*jamming_A
        noise_real=np.random.normal(0,0.01,len(cur_sig))
        noise_imag=np.random.normal(0,0.01,len(cur_sig))
        cur_sig=cur_sig+noise_real+1j*noise_imag+cur_jamming_sig
        cur_sig=cur_sig.astype('c8')
            
        np.ndarray.tofile(cur_sig,fid)
        
        print("%20s finish sec:%d"%(filename,i))
        fid.close()


# # simple generate
# filename="../data/sim_40dB_3000Hz.dat"
# generate_sim_sig(filename,10,2,34,1e6,3000,0,6e6,40)

for freq_shift in range(1080,1081,1):
    filename="e:/data/sig_codejam_40dB_0bitshift_"+str(freq_shift)+"freqshift_perHz.dat"
    generate_sim_sig(filename,5,2,34,1e6,freq_shift,0,6e6,40)