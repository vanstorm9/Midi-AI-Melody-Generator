import midi
from midiutil.MidiFile import MIDIFile
import numpy as np
import os
import os.path

#path = 'example.mid'
#path = 'Songs/Suteki-Da-Ne.mid'
#path = 'Songs/Mozart-Movement.mid'
#path = 'Songs/beethoven_ode_to_joy.mid'
#path = 'Songs/twinkle_twinkle.mid'
#path = 'Songs/grenade.mid

slash = '/'

print 'Extracting all of pattern[1]'
# Instantiate a MIDI Pattern (contains a list of tracks)
pat = midi.Pattern()

#folder_trans = 'training-songs'
#folder_trans = 'training-ground'
folder_trans = 'vocaloid-training-ground'
#folder_trans = 'training-video-test'
#folder_trans = 'training-kid-songs'
#folder_trans = 'training-classical-songs'

num_files = len([f for f in os.listdir(folder_trans)
                    if os.path.isfile(os.path.join(folder_trans, f))])

#path_ar = ['Songs/twinkle_twinkle.mid', 'Songs/Suteki-Da-Ne.mid']

def tick_to_time(tick):

    if tick !=0:
        time = 60000/(tick*192)
    else:
        time = 0
    return time

def pitch_prev_array_add(pitch, pitch_ar):
    if pitch_ar == None:
        pitch_ar = np.array([pitch])
    else:
        pitch_ar = np.concatenate((pitch_ar, np.array([pitch])))
    return pitch_ar

def tick_regulate(tick):
    if tick < 0:
        tick = 0
    
    if tick > 20:
        tick = tick/10
        #if tick_n > 256:
        #    tick_n = tick_n/5
    
    return tick

def velocity_regulate(velocity):
    # To remove negative numbers and turn them into zero
    # Also to prevent program from crashing since it only accepts numbers
    # below 256
    
    if velocity < 0:
        velocity = 0

    
    if velocity > 255:
        velocity = velocity/10
        if velocity > 256:
            velocity = velocity/4
    
    
    if velocity > 1000:
        velocity = 100
    '''
    elif velocity > 30:
        velocity = velocity/10
    '''

    return velocity

def pitch_regulate(pitch):
    if pitch < 0:
        pitch = 0
    '''
    if pitch > 256:
        pitch = pitch/10
    if pitch < 100 and pitch > 0:
        pitch = pitch + 100
        if pitch > 256:
            pitch = pitch/5
    '''
    return pitch


def pitch_prev_array_add(pitch, pitch_ar):
    if pitch_ar == None:
        pitch_ar = np.array([pitch])
    else:
        pitch_ar = np.concatenate((pitch_ar, np.array([pitch])))
    return pitch_ar


def tranverse_all_folders(folder_trans):
    j = 0
    for path in os.listdir(folder_trans):
        pattern = midi.read_midifile(folder_trans + slash + path)
        print folder_trans + slash + path
        # Instantiate a MIDI Track (contains a list of MIDI events)
        track = midi.Track()
        # Append the track to the pattern
        pat.append(track)
        # Goes through extracted song and reconstruct them (pattern[1])
        '''
        tr = 1
        start_val = 1
        i = 1
        '''
        # World is MIne sample window
        
        tr = 0
        start_val = 14
        i = 14
        #print pattern
        '''
        # Suteki Da Ne sample window
        tr = 1
        start_val = 1
        i = 1
        '''
        while True:
            #print i
            #if i > len(pattern[tr]) - 2:
            if i > len(pattern[tr]) - 2:
                break
            #print pattern[tr][i]
            tick = pattern[tr][i].tick
            pitch = pattern[tr][i].data[0]

            # Because some pattern[][].data does not have a second array element
            if len(pattern[tr][i].data) == 2:
                velocity = pattern[tr][i].data[1]
            else:
                velocity = 0
            # Place all of tick, pitch, and velocity values in indiviudal vectors
            tick = np.array([tick])
            pitch = np.array([pitch])
            velocity = np.array([velocity])
            if i == start_val:
                tick_ar = tick
                pitch_ar = pitch
                velocity_ar = velocity
            else:
                tick_ar = np.concatenate((tick_ar, tick))
                pitch_ar = np.concatenate((pitch_ar, pitch))
                velocity_ar = np.concatenate((velocity_ar, tick))
            # To reconstruct the entire song in its (piano-like) original form
            #track.append(midi.NoteOnEvent(tick= tick, channel=1, data=[pitch, velocity]))
            i = i + 1
        j = j + 1
    return pattern, tick_ar, velocity_ar, pitch_ar




# Go through all folders and form the matrix
pattern, tick_ar, velocity_ar, pitch_ar = tranverse_all_folders(folder_trans)



print 'Converting data to list. . .'

# Extract the first 30 elements of the data vector, then convert to list

window_len = 120
#window_len = 70

tick_data = tick_ar[:window_len].tolist()
pitch_data = pitch_ar[:window_len].tolist()
velocity_data = velocity_ar[:window_len].tolist()

print 'Data Converted'


# Put time series into a supervised dataset, where the target for
# each sample is the next sample

from pybrain.datasets import SequentialDataSet
from itertools import cycle

INPUT = 3
HIDDEN_LAYERS = 5
OUTPUT = 3


ds = SequentialDataSet(INPUT, OUTPUT)


# Adding sequence of numbers (of both features) into neural network
for (sample, next_sample, sam_v, next_sam_v, sam_t, next_sam_t) in zip(pitch_data, cycle(pitch_data[1:]), velocity_data, cycle(velocity_data[1:]), tick_data, cycle(tick_data[1:])):
    #ds.addSample((sample, velocity_data[i], tick_data[i]), next_sample)
    ds.addSample((sample, sam_v, sam_t), (next_sample, next_sam_v, next_sam_t))


# Build a simple LSTM networ end of the song somewhere around last 15 sec when my line pop. stupid friend decide it is a good time to send LL stickerk with 1 input node, 5 LSTM cells and 1 output node:

from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules import LSTMLayer

print 'Constructing neutral network. . .'
net = buildNetwork(
    INPUT,
    HIDDEN_LAYERS,
    OUTPUT,
    hiddenclass=LSTMLayer,
    outputbias=False,
    recurrent=True,
    )

# Train the network

from pybrain.supervised import RPropMinusTrainer
from sys import stdout


print 'Starting to train neural network. . .'
trainer = RPropMinusTrainer(net, dataset=ds)
train_errors = []  # save errors for plotting later
EPOCHS_PER_CYCLE = 5
#CYCLES = 200
CYCLES = 100
EPOCHS = EPOCHS_PER_CYCLE * CYCLES
print 'Entering loop. . .'
for i in xrange(CYCLES):
    # Does the training
    trainer.trainEpochs(EPOCHS_PER_CYCLE)
    train_errors.append(trainer.testOnData())
    epoch = (i + 1) * EPOCHS_PER_CYCLE
    print 'i: ', i
    print ('\r epoch {}/{}'.format(epoch, EPOCHS))

    stdout.flush()
print 'Exit loop'
print ''

print 'final error =', train_errors[-1]

# Plot the errors (note that in this simple toy example,
# we are testing and training on the same dataset, which
# is of course not what you'd do for a real project!):

import matplotlib.pyplot as plt

plt.plot(range(0, EPOCHS, EPOCHS_PER_CYCLE), train_errors)
plt.xlabel('epoch')
plt.ylabel('error')
plt.show()

# Now ask the network to predict the next sample
'''
for (sample, target) in ds.getSequenceIterator(0):
    print '               sample = %4.1f' % sample
    print 'predicted next sample = %4.1f' % net.activate(sample)
    print '   actual next sample = %4.1f' % target
    print ''
'''


# Start constructing the new song (Midiutil version)
MyMIDI = MIDIFile(1)
track = 0   
time = 0
MyMIDI.addTrackName(track,time,"Sample Track")
#tempo = 120
tempo = 120
MyMIDI.addTempo(track,time,tempo)



i = 0
time = 0
prev_pitch_ar = np.array([])

# Preform seeding (although seeding is not random, it seeds the original midi song)
for (sample, target) in ds.getSequenceIterator(0):
    #print track_fi

    # Part of code used to have generator predict based on its own prev notes
    '''
    if i != 0:
        sample = prev_ac_ar
    '''
    
    pred_ar = net.activate(sample)

    tick_n = tick_regulate(int(pred_ar[2]))
    pitch_n = pitch_regulate(int(pred_ar[0]))
    velocity_n = velocity_regulate(int(pred_ar[1]))




    
    if i == 0:    
        prev_pitch_ar = pitch_prev_array_add(pitch_n, None)
    else:
        prev_pitch_ar = pitch_prev_array_add(pitch_n, prev_pitch_ar)
    
    
    
    #print '               sample = ', sample
    print 'predicted next sample = ', pitch_n, ' ', velocity_n, ' ', tick_n 
    #print '   actual next sample = ', target
    print ''

    # Part of code used to have generator predict based on its own prev notes
    #prev_ac_ar = np.array([pitch_n, velocity_n, tick_n])

    '''
    if i > 2:
        track_fi.append(midi.NoteOffEvent(tick= tick_n, channel=1, data=[prev_pitch_ar[i - 3], 0]))
    '''

    
    
    i = i + 1
    

    # Add a note. addNote expects the following information:

    #duration = 1
    #volume = 100
    
    track = 0
    channel = 0
    pitch = pitch_n
    duration = tick_n/5
    volume = velocity_n

    #time = tick_to_time(tick_n)
    
    time = tick_to_time(tick_n)
    
    MyMIDI.addNote(track,channel,pitch,time,duration,volume)           

    


    '''
    # To add previous pitch from 2 notes ago
    if i > 6:
        MyMIDI.addNote(track,channel,prev_pitch_ar[i-4],time,duration,volume) 
    '''

binfile = open("result.mid", 'wb')
MyMIDI.writeFile(binfile)
binfile.close()
print 'Finished writing Midi file'

print 'Midi file was written'
