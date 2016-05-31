import midi
from midiutil.MidiFile import MIDIFile
import numpy as np
import os
import os.path



import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, LSTM


slash = '/'

print 'Extracting all of pattern[1]'
# Instantiate a MIDI Pattern (contains a list of tracks)
pat = midi.Pattern()

#folder_trans = 'training-songs'
#folder_trans = 'training-ground'
folder_trans = '../vocaloid-training-ground'
#folder_trans = 'training-video-test'
#folder_trans = 'training-kid-songs'
#folder_trans = 'training-classical-songs'

num_files = len([f for f in os.listdir(folder_trans)
                    if os.path.isfile(os.path.join(folder_trans, f))])

#path_ar = ['Songs/twinkle_twinkle.mid', 'Songs/Suteki-Da-Ne.mid']


# since we are using stateful rnn tsteps can be set to 1
tsteps = 1
batch_size = 23
epochs = 30
# number of elements ahead that are used to make the prediction
lahead = 1



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


pitch_ar_out = np.expand_dims(pitch_ar, axis=1)
pitch_ar = np.expand_dims(np.expand_dims(pitch_ar, axis=1), axis=1)


print pitch_ar.shape
print pitch_ar_out.shape
print 'Converting data to list. . .'




model = Sequential()
model.add(LSTM(50,
               batch_input_shape=(batch_size, tsteps, 1),
               return_sequences=True,
               stateful=True))
model.add(LSTM(50,
               batch_input_shape=(batch_size, tsteps, 1),
               return_sequences=False,
               stateful=True))
model.add(Dense(1))
model.compile(loss='mse', optimizer='rmsprop')

print('Training')
for i in range(epochs):
    print('Epoch', i, '/', epochs)
    model.fit(pitch_ar,
              pitch_ar_out,
              batch_size=batch_size,
              verbose=1,
              nb_epoch=1,
              shuffle=False)
    model.reset_states()

print('Predicting')
predicted_output = model.predict(pitch_ar, batch_size=batch_size)

print('Ploting Results')
plt.subplot(2, 1, 1)
plt.plot(pitch_ar_out)
plt.title('Expected')
plt.subplot(2, 1, 2)
plt.plot(predicted_output)
plt.title('Predicted')
plt.show()



















