import numpy as np
import pandas as pd
from collections import Counter
from numpy.random import multinomial as randm
from numpy import where
import scipy.signal as si
import IPython.display as ipd
import librosa
import scipy
from matplotlib import patches
import librosa.display as ld
from music21 import midi as midi21
from music21 import stream
from jchord.progressions import ChordProgression
import copy
import matplotlib.pyplot as plt
import music21
from music21 import converter,instrument 
import music21.note as note
from music21 import converter, note, stream, meter
import random

numbNotes = 25
numbDuras = 5
length = 150


###convert note into integers
def noteToInt (note):
    return{
        'C'  :0,
        'C#' :1,
        'D'  :2,
        'E-' :3,
        'E'  :4,
        'F'  :5,
        'F#' :6,
        'G'  :7,
        'G#' :8,
        'A'  :9,
        'A#' :10,
        'B'  :11,
        'Cm' :12,
        'C#m':13,
        'Dm' :14,
        'D#m':15,
        'Em' :16,
        'Fm' :17,
        'F#m':18,
        'Gm' :19,
        'G#m':20,
        'Am' :21,
        'A#m':22,
        'Bm' :23,
        'rest':24,
        'Em7':16,
        'A7' :9,
        'Dm7':14,
        'G7' :7,
     'A7sus4':9,
        'Gm6':19,
        'C7' :0,
      'Fsus4':5  
    }.get(note,24)

###convert number to note
def numberToNote(number):
    return{
        0:'C' ,
        1:'C#',
        2: 'D',
        3:'D#' ,
        4:'E'  ,
        5:'F'  ,
        6:'F#' ,
        7:'G' ,
        8:'G#',
        9:'A' ,
        10:'A#' ,
        11:'B'  ,
        12:'Cm' ,
        13:'C#m',
        14:'Dm' ,
        15:'D#m',
        16:'Em',
        17:'Fm',
        18:'F#m',
        19:'Gm' ,
        20:'G#m',
        21:'Am' ,
        22:'A#m',
        23:'Bm' ,
        24: 'rest'  
    }.get(number,'C')

###convert duration to  number
def duraToInt(dura):
    return{
        '16th':0,
        'eighth':1,
        'quarter':2,
        'half':3,
        'whole':4,
        }.get(dura,2)

###convert number to duration
def intToDura(number):
    return{
        0:'16th',
        1:'eighth',
        2:'quarter',
        3:'half',
        4:'whole',
        }.get(number,'quarter')

###----------plotting probability graph
def plot_transition_matrix(A, ax=None, xlabel='State $a_j$', ylabel='State $a_i$', title='', clim=[-6, 0], cmap='gray_r'):
    
    im = plt.imshow(A, origin='lower', aspect='auto', cmap=cmap)
    im.set_clim([0, 1])
    cbar = plt.colorbar(im)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    cbar.ax.set_ylabel('Probability')
    
    chroma_label = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    chord_label_maj = chroma_label
    chord_label_min = [s + 'm' for s in chroma_label]
    chord_labels = chord_label_maj + chord_label_min
    chord_labels_squeezed = chord_labels.copy()
    for k in [13, 15, 17, 18, 20, 22]:
        chord_labels_squeezed[k] = ''
        
    chord_labels_squeezed.append('rest')
    chord_labels.append('rest')
    plt.xticks(np.arange(25), labels=chord_labels_squeezed )
    plt.yticks(np.arange(25), labels=chord_labels)
    
    return im






###----------training notes-----------####
def trainNotes(element, HMM, HM2):    
    gNotes =[]
    for i in range (len(element)):
        gNotes.append( str(element[i].name))
    #print("print gnotes " ,gNotes)
    ###proability table
    ###HMM = np.zeros((numbNotes, numbNotes))
    ###sum of each note
    ###HM2=np.zeros(numbNotes)    
    ### generate frequency of each note
    for i in range(len(gNotes)):
        HM2[  noteToInt(gNotes[i]) ]+=1
    ###generate possibility table
    for i in range(len(gNotes) - 1):
        x= noteToInt(gNotes[i])
        y= noteToInt(gNotes[i+1])
        HMM[x][y]+=(1/HM2[x])
    
   


#------generating notes-------###
def generateNotes(HMM, HM2, length):
    #to store generated notes
    returnNotes = []
    #temporay store next note
    buffer = []
    ###generate all possible notes
    measures = [None] * numbNotes
    for i in range(numbNotes):
        measures[i]=numberToNote(i)
    #generate song with same number of notes
    chord = 'C'
    for i in range(length):        
        buffer = random.choices(measures,weights=HMM[noteToInt(chord)], k=1)        
        chord = buffer[0]
        returnNotes.append(buffer[0])
    
    return returnNotes
    
    

###------training duration---------###
def trainDuration(element, HMM2, HM22):
    gDura =[]    
    for i in range (len(element)):
        gDura.append(element[i].duration.type)
    ### generate frequency of each duration
    for i in range(len(gDura)):
        HM22[  duraToInt(gDura[i]) ]+=1
    
    ### generate possibility table
    for i in range(len(gDura) - 1):
        x= duraToInt(gDura[i])
        y= duraToInt(gDura[i+1])
        HMM2[x][y]+=(1/HM22[x])
    
   
    

###-------generating duration-----###
def generateDuration(HMM2, HM22,length):
    returnDuras = []
    #temporay store next duration
    buffer = []
    ###generate song with same number of dura
    ###generate all possible rythm
    measures = [None] * numbDuras
    for i in range(numbDuras):
        measures[i]=intToDura(i)
    dura = "quarter"
    for i in range(length):
        buffer = random.choices(measures,weights=HMM2[duraToInt(dura)], k=1)
        dura = buffer[0]
        returnDuras.append(buffer[0])
    return returnDuras



###---------reading from a file------------####
components = [] 
chords = []
notes = []
durations = []
notes2 = []
instrumList = []

import os

path = 'C:\\Users\\conan\\Desktop\\cse190\\final project\\MIDI Files\\MIDI Files\\The Wind Waker\\'
folder = os.fsencode(path)
filenames = []


for files in os.listdir(folder):
    filename = os.fsdecode(files)
    if filename.endswith( ('.mid') ):
        filenames.append(filename)

filenames.sort()

midi_dict = {}

for i in filenames:
    file = converter.parse(path+i)
    instruments = instrument.partitionByInstrument(file)
    instrument_dict = {}

    for j in instruments.parts:    
        key = j.id
        notes_list = [] 
        for k in j.notes:
            if k.isNote or k.isRest:
                notes_list.append(k)
                    
            instrument_dict[key] = notes_list
        
    midi_dict[i] = instrument_dict


'''
###---------for reading testing------------####
components = [] 
chords = []
notes = []
durations = []
notes2 = []
instrumList = []

path = 'C:\\Users\\conan\\Desktop\\cse190\\final project\\MIDI Files\\MIDI Files\\Oracle of AgesISeasons\\'
songChoose = 'prelude6.mid'
file = converter.parse(path+songChoose)
instruments = instrument.partitionByInstrument(file)

instrument_dict = {}

for i in instruments.parts:    
    key = i.id
    print(key)
    notes_list = []
    for j in i.notes:
        if j.isNote or j.isRest:
            #print(j)
            notes_list.append(j)
    instrument_dict[key] = notes_list

'''
###-----------------------------generating song----------------###


###proability table for notes
H1 = np.zeros((numbNotes, numbNotes))
###sum of each note
HH1=np.zeros(numbNotes)

###proability table for duration
D1 = np.zeros((numbDuras, numbDuras))
###sum of each duration
DD1=np.zeros(numbDuras)

###proability table for notes
H2 = np.zeros((numbNotes, numbNotes))
###sum of each note
HH2=np.zeros(numbNotes)

###proability table for duration
D2 = np.zeros((numbDuras, numbDuras))
###sum of each duration
DD2=np.zeros(numbDuras)

###proability table for notes
H3 = np.zeros((numbNotes, numbNotes))
###sum of each note
HH3=np.zeros(numbNotes)

###proability table for duration
D3 = np.zeros((numbDuras, numbDuras))
###sum of each duration
DD3=np.zeros(numbDuras)


#----store generated notes and duration-----#
notes3 = []
dura3 =  []
notes4 = []
dura4 = []
notes5 = []
dura5 = []

instrument1= 'Bassoon'
instrument2= 'Vibraphone'
instrument3= 'Xylophone'

instrument_list = [instrument1, instrument2, instrument3]
H_list = [H1, H2, H3, HH1, HH2, HH3]
D_list = [D1, D2, D3, DD1, DD2, DD3]

###-------------------reading files----------###
for key in midi_dict:
    for key2 in midi_dict[key]:
        for instru in instrument_list:
            if key2 == instru:
                for i in range(int(len(H_list)/2)):
                    trainNotes(midi_dict[key][key2], H_list[i], H_list[i+3])
                    trainDuration(midi_dict[key][key2], D_list[i], D_list[i+3])

'''
###------training notes and duration--------------##
trainNotes(instrument_dict[instrument1], H1, HH1)
trainDuration(instrument_dict[instrument1], D1, DD1)
trainNotes(instrument_dict[instrument2], H2, HH2)
trainDuration(instrument_dict[instrument2], D2, DD2)
trainNotes(instrument_dict[instrument3], H3, HH3)
trainDuration(instrument_dict[instrument3], D3, DD3)
'''

###---------generate notes and duration-----------##
notes3 = generateNotes( H1, HH1, length)
dura3 = generateDuration(D1, DD1, length)
notes4 = generateNotes( H2, HH2,length)
dura4 = generateDuration(D2, DD2, length)
notes5 = generateNotes(H3, HH3, length)
dura5 = generateDuration( D3, DD3, length)

plot_transition_matrix(H1)




m3 = stream.Part()
m4 = stream.Part()
m5 = stream.Part()
m3.insert(instrument.Bassoon())
m4.insert(instrument.Vibraphone())
m5.insert(instrument.Xylophone())


#----adding notes to track------#
for i in range(len(notes3) - 1):
    if(notes3[i] == 'rest'):
        newNote= note.Rest()
        newNote.duration.type = dura3[i]
        m3.append(newNote)
        continue
    newNote = note.Note(notes3[i])
    newNote.duration.type = dura3[i]
    m3.append(newNote)


for i in range(len(notes4) - 1):
    if(notes4[i] == 'rest'):
        newNote= note.Rest()
        newNote.duration.type = dura4[i]
        m4.append(newNote)
        continue
    newNote = note.Note(notes4[i])
    newNote.duration.type = dura4[i]
    m4.append(newNote)


for i in range(len(notes5) - 1):
    if(notes5[i] == 'rest'):
        newNote= note.Rest()
        newNote.duration.type = dura5[i]
        m5.append(newNote)
        continue
    newNote = note.Note(notes5[i])
    newNote.duration.type = dura5[i]
    m5.append(newNote)



#-----adding tracks to song------------#
song = stream.Score()
song.insert(0,m3)
song.insert(0,m4)
song.insert(0,m5)

#song.write('midi', 'blah.mid')
#song.show('midi')





        
