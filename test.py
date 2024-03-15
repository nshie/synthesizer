import numpy as np
from scipy import signal
import pyaudio
import time
import matplotlib.pyplot as plt

SAMPLE_RATE = 44100
MIN_FREQUENCY = 100
MIN_BUFFER_SIZE = int(SAMPLE_RATE / MIN_FREQUENCY)

numCycles = 100
newTime = np.linspace(0 / MIN_FREQUENCY, (numCycles + 1) / MIN_FREQUENCY, MIN_BUFFER_SIZE * numCycles, endpoint=False)
#newTime = np.linspace(0, (5 + 1) / self.MIN_FREQUENCY, self.MIN_BUFFER_SIZE, endpoint=False)
wf = np.sin(440 * 2 * np.pi * newTime)
wf += np.sin(440 * (2 ** (7/12)) * 2 * np.pi * newTime)

wf = wf / 2

plt.plot(wf)
plt.axis([0, 1000, -5, 5])
plt.show()

cycle = 0

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

def generateTimeArray(self, cycle):
    out = np.linspace(cycle / MIN_FREQUENCY, (cycle + 1) / MIN_FREQUENCY, MIN_BUFFER_SIZE, endpoint=False)
    return out

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    '''
    global cycle
    startIndex = cycle * MIN_BUFFER_SIZE
    endIndex = (cycle + 1) * MIN_BUFFER_SIZE
    data = np.zeros(1)
    if endIndex < len(wf):
        data = wf[startIndex:endIndex]
    cycle += 1

    bytestream = (data * 32767).astype("<h").tobytes()
    return (bytestream, pyaudio.paContinue)
    '''
    t = np.linspace(0, MIN_DURATION, MIN_BUFFER_SIZE, endpoint=False)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(width=2),
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True,
                    frames_per_buffer=MIN_BUFFER_SIZE,
                    stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)

while stream.is_active():
    time.sleep(0.1)

    
# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()
