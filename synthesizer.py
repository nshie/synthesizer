import wave
import numpy as np
from scipy import signal
import pyaudio



class Synthesizer():
    SAMPLE_RATE = 44100
    MIN_FREQUENCY = 60
    MIN_DURATION = 1/MIN_FREQUENCY
    MIN_BUFFER_SIZE = int(SAMPLE_RATE * MIN_DURATION)

    '''
    C       C#      D       D#      E       F       F#      G       G#      A       A#      B '''
#3                                                                          0       1       2
    pitchFrequencies = [                                                    220.00, 233.08, 246.94,
#4  3       4       5       6       7       8       9       10      11      12      13      14
    261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88,
#5  15      16      17      18      19      20      21      22      23      24      25      26
    523.25, 554.37, 587.33, 622.25, 659.25, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77,
#6  27      28      29      30      31      32      33      34      35      36      37      38
    1046.50,1108.73,1174.66,1244.51,1318.51,1396.91,1479.98,1567.98,1661.22,1760.00,1864.66,1975.53,
#7  39
    2093.00
    ]

    A3 = 0;  Bb3 = 1;  B3 = 2
    C4 = 3;  Db4 = 4;  D4 = 5;  Eb4 = 6;  E4 = 7;  F4 = 8;  Gb4 = 9;  G4 = 10; Ab4 = 11; A4 = 12; Bb4 = 13; B4 = 14
    C5 = 15; Db5 = 16; D5 = 17; Eb5 = 18; E5 = 19; F5 = 20; Gb5 = 21; G5 = 22; Ab5 = 23; A5 = 24; Bb5 = 25; B5 = 26
    C6 = 27; Db6 = 28; D6 = 29; Eb6 = 30; E6 = 31; F6 = 32; Gb6 = 33; G6 = 34; Ab6 = 35; A6 = 36; Bb6 = 37; B6 = 38
    C7 = 39

    pya = None
    stream = None

    armed = False

    # An on-going array tracking time
    cycles = 0
    #startT = np.linspace(0, (MIN_BUFFER_SIZE / SAMPLE_RATE), MIN_BUFFER_SIZE, endpoint=False)
    t = np.linspace(0, MIN_DURATION, MIN_BUFFER_SIZE, endpoint=False)

    # Controlling the sound
    notesPlaying = [False] * len(pitchFrequencies)
    volume = 1
    cutoff = 1
    waveforms = ["Sine", "Saw", "Square", "Triangle"]
    SINE = 0; SAW = 1; SQUARE = 2; TRIANGLE = 3
    oscillator1Waveform = SINE
    oscillator2Waveform = SINE
    oscillator1Pitch = 0
    oscillator2Pitch = 0
    oscillatorRatio = 0.5

    # Declicking
    buffer = np.zeros(MIN_BUFFER_SIZE)
    

    ''' <-------------------- INTERNAL FUNCTIONS --------------------> '''
    # Returns a numpy array with the same size as t
    def wave(self, frequency):
        wave = 0

        inputArray1 = 2 * np.pi * frequency * self.t * self.dollarsToFrequencyRatio(self.oscillator1Pitch)

        match self.oscillator1Waveform:
            case self.SINE:
                wave = np.sin(inputArray1) * self.oscillatorRatio
            case self.SAW:
                wave = signal.sawtooth(inputArray1) * self.oscillatorRatio
            case self.SQUARE:
                wave = signal.square(inputArray1) * self.oscillatorRatio
            case self.TRIANGLE:
                wave = signal.sawtooth(inputArray1) * self.oscillatorRatio
            case _:
                pass

        inputArray2 = 2 * np.pi * frequency * self.t * self.dollarsToFrequencyRatio(self.oscillator2Pitch)

        match self.oscillator2Waveform:
            case self.SINE:
                wave += np.sin(inputArray2) * (1 - self.oscillatorRatio)
            case self.SAW:
                wave += signal.sawtooth(inputArray2) * (1 - self.oscillatorRatio)
            case self.SQUARE:
                wave += signal.square(inputArray2) * (1 - self.oscillatorRatio)
            case self.TRIANGLE:
                wave += signal.sawtooth(inputArray2, 0.5) * (1 - self.oscillatorRatio)
            case _:
                pass

        return wave

    def generateTimeArray(self, cycle):
        return np.linspace(cycle / self.MIN_FREQUENCY, (cycle + 1) / self.MIN_FREQUENCY, self.MIN_BUFFER_SIZE, endpoint=False)

    # a fun nod to the fact that values being passed in are 100 cents and not 1 cent
    def dollarsToFrequencyRatio(self, dollars):
        return 2 ** (dollars / 12)

    ''' <-------------------- EXTERNAL FUNCTIONS --------------------> '''
    def arm(self):
        if (self.armed):
            return
        
        self.t = self.generateTimeArray(0)
        self.cycles = 0

        self.pya = pyaudio.PyAudio()
        
        def callback(in_data, frame_count, time_info, status):
            wave = np.zeros(self.MIN_BUFFER_SIZE)

            # sum the notes being played
            for i in range(len(self.pitchFrequencies)):
                if (self.notesPlaying[i] == True):
                    newWave = self.wave(self.pitchFrequencies[i])
                    wave = np.add(wave, newWave)

            # normalize
            maxAmplitude = wave.max()
            if (not maxAmplitude == 0):
                wave = wave / wave.max() * self.volume

            print(f"{self.t[-1] - (self.cycles + 1 - 1/self.SAMPLE_RATE) / self.MIN_FREQUENCY}")

            self.cycles += 1
            self.t = self.generateTimeArray(self.cycles)#np.linspace(self.cycles / self.MIN_FREQUENCY, (self.cycles + 1) / self.MIN_FREQUENCY, self.MIN_BUFFER_SIZE)
            #self.t = np.linspace(self.cycles / self.MIN_FREQUENCY, (self.cycles + 1) / self.MIN_FREQUENCY, self.MIN_BUFFER_SIZE)
            #print(self.t)

            bytestream = (wave * 32767).astype("<h").tobytes()
            return (bytestream, pyaudio.paContinue)

        self.stream = self.pya.open(format=self.pya.get_format_from_width(width=2),
                        channels=1,
                        rate=self.SAMPLE_RATE,
                        output=True,
                        frames_per_buffer=self.MIN_BUFFER_SIZE,
                        stream_callback=callback)
    
        self.armed = True
        print("Arming synthesizer...")

    def dearm(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.pya:
            self.pya.terminate()

        self.armed = False
        print("De-arming synthesizer...")

    def playNote(self, note):
        if not self.armed:
            return

        if note < 0 or note >= len(self.pitchFrequencies):
            return

        #E[:SAMPLE_RATE * duration // 2] = 0

        #samplerate, reverbIR = wavfile.read('ConradPrebysConcertHallSeatF111.wav')
        #reverbIR = reverbIR[ : , 0]
        #reverbIRFloat = reverbIR.astype(np.float32)
        #reverbIRFloat = reverbIRFloat / reverbIRFloat.max()

        self.notesPlaying[note] = True


    def stopNote(self, note):
        if note < 0 or note >= len(self.pitchFrequencies):
            return

        self.notesPlaying[note] = False

    def setVolume(self, value):
        self.volume = value
        print(f'set synthesizer volume to {value}')

    def setOscillator1Waveform(self, waveform):
        self.oscillator1Waveform = waveform

    def setOscillator2Waveform(self, waveform):
        self.oscillator2Waveform = waveform

    def setOscillator1Pitch(self, cents):
        self.oscillator1Pitch = cents

    def setOscillator2Pitch(self, cents):
        self.oscillator2Pitch = cents

    def setOscillatorRatio(self, percentage):
        self.oscillatorRatio = max(0, min(percentage, 1))

    def setCutoff(self, percentage):
        pass
    
    '''
    duration = 3
    t = np.linspace(0, duration, SAMPLE_RATE * duration)
    Ahz = 440
    A = 0.25 * np.sin(2 * np.pi * Ahz * t)
    C = 0.25 * np.sin(2 * np.pi * Ahz * 6 / 5 * t)
    E = 0.25 * np.sin(2 * np.pi * Ahz * 1.5 * t)
    #E[:SAMPLE_RATE * duration // 2] = 0

    SAMPLE_RATE, reverbIR = wavfile.read('ConradPrebysConcertHallSeatF111.wav')
    reverbIR = reverbIR[ : , 0]
    #reverbIRFloat = reverbIR.astype(np.float32)
    #reverbIRFloat = reverbIRFloat / reverbIRFloat.max()

    compose = A + C + E
    #compose[SAMPLE_RATE:duration * SAMPLE_RATE] = 0

    rawMax = compose.max()

    #Compose = np.fft.rfft(compose)
    #ReverbFR = np.fft.rfft(reverbIR)
    #desiredLength = len(Compose) + len(ReverbFR) - 1
    #Compose = np.pad(Compose, (0, desiredLength - len(Compose)), 'constant')
    #ReverbFR = np.pad(ReverbFR, (0, desiredLength - len(ReverbFR)), 'constant')

    #Filtered = Compose * ReverbFR

    #compose = np.fft.irfft(Filtered)

    compose = np.convolve(compose, reverbIR, 'full')
    compose = compose[len(reverbIR) : ]
    compose = compose * (rawMax / compose.max())

    # Put the audio together with shape (1, 44100).
    audio = np.array([compose]).T

    # Convert to (little-endian) 16 bit integers.
    audio = (audio * (2 ** 15 - 1)).astype("<h")

    with wave.open("sound1.wav", "w") as f:
        # 2 Channels.
        f.setnchannels(1)
        # 2 bytes per sample.
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(audio.tobytes())
    '''
