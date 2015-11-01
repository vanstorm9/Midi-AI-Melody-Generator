import mido
from mido import MidiFile
from mido.midifiles import MidiTrack
from mido import Message

#pattern = MidiFile('Songs/Suteki-Da-Ne.mid')
pattern = MidiFile('Songs/twinkle_twinkle.mid')
mid = MidiFile()


tracks = MidiTrack()
tracks.append(tracks)
'''
for message in pattern:
    
    
    if message.type == 'note_on' or message.type == 'note_off':
        #print message
        mid.tracks.append(mid.Message(message.type, note=message.note, velocity=message.velocity, time=message.time))
    #elif message.type == 'control_change':
    #    mid.tracks.append(Message(message.type, control=message.control, value=message.value, time=message.time))
    
    #else:
    #    print message
    #    print message.type
    
    
    #tracks.append(Message(message.type, note=message.note, velocity=message.velocity, time=message.time))
    #tracks.append(message)

'''

for message in pattern:
    

    if message.type == 'note_on' or message.type == 'note_off':
        print message
        tracks.append(Message(message.type, note=message.note, velocity=message.velocity, time=message.time))

    
    
mid.save('result.mid')
print 'New midi file saved!'

