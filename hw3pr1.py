# -*- coding: utf-8 -*-
import random
import math
from csaudio import play, readwav, writewav
from copy import deepcopy
import os
import wave
wave.big_endian = 0


def scale(L, scale_factor):
    '''Given a list L, scales each element of the list by scale_factor'''

    return [scale_factor * n for n in L]

def wrap1( L ):
    """ Given a list L, shifts each element in L to the right by 1 
        (the element at the end of the list wraps around to the beginning)
    """

    # I changed the body of this function to call wrapN, 
    # so that I can reuse the code I wrote for that problem 
    return wrapN(L, 1)   


def wrapN(L, N):
    """ Given a list L, shifts each element in L to the right by N 
        (elements at the end of the list wrap around to the beginning)
    """

    length = len(N)
    return [ L[i-N] for i in range(length) ]


def add_2(L, M):
    '''Given two lists, L and M, adds their respective elements. If the two 
       lists have different lengths, the function truncates the result so that 
       it is as long as the shorter list.
    '''

    length = min(len(L), len(M))  # find the shorter length
    return [ L[i] + M[i] for i in range(length) ]

    # Here's an alternative solution that uses the built-in zip function,
    # which truncates for us and creates tuples of the corresponding elements.
    #return [l + m for (l, m) in zip(L, M)]    


def add_scale_2(L, M, L_scale, M_scale):
    '''Given two lists, L and M, and two scale factors, L_scale and M_scale, 
       scales each list by its respective scale factor, then adds the 
       results, pairwise. If the two  lists have different lengths, the function 
       truncates the result so that it is as long as the shorter list.
    '''

    return add_2(scale(L, L_scale), scale(M, M_scale))  # yay for code re-use!


# generalized versions of add_2 and add_scale_2

def add_N(lists):
    '''Given a list of lists, adds their respective elements. If the two 
       lists have different lengths, the function truncates the result so that 
       it is as long as the shortest list.
    '''

    return map(sum, apply(zip, lists)) # lots of higher-order functions here!


def add_scale_N(lists, scaleFactors):
    '''Given a list of lists and a list of scale factors, scales each list by 
       its respective scale factor, then sums the results, element-wise. If the 
       lists have different lengths, the function  truncates the result so that 
       it is as long as the shortest list.
    '''
    
    scaledLists = [scale(l, f) for (l, f) in zip(lists, scaleFactors)]
    return add_N(scaledLists)


# Helper function:  randomize
def randomize( x, chance_of_replacing ):
    """ randomize takes in an original value, x
        and a fraction named chance_of_replacing.

        With the "chance_of_replacing" chance, it
        should return a random float from -32767 to 32767.

        Otherwise, it should return x (not replacing it).
    """
    r = random.uniform(0,1)
    if r < chance_of_replacing:
        return random.uniform(-32768,32767)
    else:
        return x
    

def replace_some(L, chance_of_replacing):
    '''Given a list L, returns a new list L' where each element in L has a 
       chance_of_replacing chance of being replaced with a random, 
       floating-point value in the range -32767 to 32767.
    '''

    return [randomize(e, chance_of_replacing) for e in L]

#
# below are functions that relate to sound-processing ...
#


# a function to make sure everything is working
def test():
    """ a test function that plays swfaith.wav
        You'll need swfailt.wav in this folder.
    """
    play( 'swfaith.wav' )

    
# The example changeSpeed function
def changeSpeed(filename, newsr):
    """ changeSpeed allows the user to change an audio file's speed
        input: filename, the name of the original file
               newsr, the *new* sampling rate in samples per second
        output: no return value; creates and plays the file 'out.wav'
    """
    samps, sr = readwav(filename)

    print "The first 10 sound-pressure samples are\n", samps[:10]
    print "The original number of samples per second is", sr
    
    newsamps = samps                        # no change to the sound
    writewav( newsamps, newsr, "out.wav" )  # write data to out.wav
    print "\nPlaying new sound..."
    play( 'out.wav' )   # play the new file, 'out.wav'
    


def flipflop(filename):
    """ flipflop swaps the halves of an audio file
        input: filename, the name of the original file
        output: no return value, but
                this creates the sound file 'out.wav'
                and plays it
    """
    print "Playing the original sound..."
    play(filename)
    
    print "Reading in the sound data..."
    samps, sr = readwav(filename)
    
    print "Computing new sound..."
    # this gets the midpoint and calls it x
    x = len(samps)/2
    newsamps = samps[x:] + samps[:x] # flip flop
    newsr = sr                       # no change to the sr
    
    writewav( newsamps, newsr, "out.wav" )
    print "Playing new sound..."
    play( 'out.wav' )

class Sound( object):
    def __init__( self, filename = None):
        if filename:
            self.samps, self.sr = readwav(filename)
        else:
            self.samps, self.sr = None, None

    @staticmethod
    def fromSamplesAndRate(samps, sr):
        new_sound = Sound()
        new_sound.samps = samps
        new_sound.sr = sr
        return new_sound

    @staticmethod
    def fromNotes(notestring, tempo):
        beat_seconds = 60. / tempo
        print beat_seconds
        split_notes = notestring.split()

        new_sound = Sound()
        new_sound.samps = []
        new_sound.sr = 44100

        previous_note_number = None

        for note_char in split_notes:
            previous_note_number = getNoteNumber(note_char, previous_note_number)
            samps, sr = gen_pure_tone(get_frequency(previous_note_number), beat_seconds)
            new_sound.append(Sound.fromSamplesAndRate(samps, sr))
            new_sound.append(silence(beat_seconds))

        return new_sound

    def clone(self):
        return deepcopy(self)

    def changeSpeed(self, newsr):
        self.sr = newsr
        return self

    def flipflop(self):
        x = len(self.samps)/2
        self.samps = self.samps[x:] + self.samps[:x]
        return self

    def reverse(self):
        self.samps = self.samps[::-1]
        return self

    def scaleVolume(self, scale = 1.):
        self.samps = [x * scale for x in self.samps]
        return self

    def staticize(self, p_static = 0.05):
        self.samps = [ random.randrange(-32768, 32767) if
                    (random.random() < p_static) else x for x in self.samps]
        return self

    def overlay(self, other):
        self.samps = map(lambda x: x/2, map(sum, zip(self.samps, other.samps)))
        return self

    def append(self, other):
        assert self.sr == other.sr, "Sample rates must match, %d != %d" % (self.sr, other.sr)
        self.samps += other.samps
        return self

    def echo(self, time_delay):
        self.samps = self.clone().delay(time_delay).overlay(self.clone().extend(time_delay))
        return self

    def delay(self, time_delay):
        self.samps = [0 for t in xrange(int(time_delay * self.sr))] + self.samps
        return self

    def extend(self, time_delay):
        self.samps = self.samps + [0 for t in xrange(int(time_delay * self.sr))]
        return self

    def write( self, filename = 'out.wav'):
        writewav( self.samps, self.sr, filename)
        return self

    def play( self):
        self.write(filename = 'temp.wav')
        play('temp.wav')
        os.remove('temp.wav')
        return self


# Helper function for generating pure tones
def gen_pure_tone(freq, seconds):
    """ pure_tone returns the y-values of a cosine wave
        whose frequency is freq Hertz.
        It returns nsamples values, taken once every 1/44100 of a second;
        thus, the sampling rate is 44100 Hertz.
        0.5 second (22050 samples) is probably enough.
    """
    sr = 44100
    # how many data samples to create
    nsamples = int(seconds*sr) # rounds down
    # our frequency-scaling coefficient, f
    f = 2*math.pi/sr           # converts from samples to Hz
    # our amplitude-scaling coefficient, a
    a = 32767.0
    # the sound's air-pressure samples
    samps = [ a*math.sin(f*n*freq) for n in range(nsamples) ]
    # return both...
    return samps, sr


def pure_tone(freq, time_in_seconds):
    """ plays a pure tone of frequence freq for time_in_seconds seconds """
    print "Generating tone..."
    samps, sr = gen_pure_tone(freq, time_in_seconds)
    print "Writing out the sound data..."
    writewav( samps, sr, "out.wav" )
    print "Playing new sound..."
    play( 'out.wav' )

note_map = {'A':1,
            'A#':2,
            'B':3,
            'C':-8,
            'C#':-7,
            'D':-6,
            'D#':-5,
            'E':-4,
            'F':-3,
            'F#':-2,
            'G':-1,
            'G#':0
            }

def getNoteNumber(note, previous_note_number = None):
    note_fully_specified = note[-1:] in map(str, range(0, 9))
    # if previous_note_number and not note_fully_specified:
    #     return 4 * 12 + note_map[note]
    #     possible = [(abs(previous_note_number - x), x)
    #         for x in range(1,88) if x % 12 == note_map[note]]
    #     return min(possible)[1]
    if note_fully_specified:
        return int(note[-1:]) * 12 + note_map[note[:-1]]
    else:
        return 4 * 12 + note_map[note]

def get_frequency(note_number):
    return int( 2.0 ** ( (note_number-49) / 12.) * 440 )

def silence(seconds):
    return Sound.fromSamplesAndRate([0 for i in xrange(int(44100*seconds))],44100)

s = Sound('swfaith.wav')
s.clone()
a = Sound.fromNotes('''A A E5 E5 F#5 F#5 E5
  D5 D5 C#5 C#5 B B A
  E5 E5 D5 D5 C#5 C#5 B
  E5 E5 D5 D5 C#5 C#5 B
  A A E5 E5 F#5 F#5 E5
  D5 D5 C#5 C#5 B B A''', 60)
