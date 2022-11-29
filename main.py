from pydub import AudioSegment
from pyannote.audio import Pipeline
import re

def prep_file():
    spacermilli = 2000
    spacer = AudioSegment.silent(duration=spacermilli)
    audio = AudioSegment.from_mp3("input.mp3") 
    audio = spacer.append(audio, crossfade=0)
    audio.export('input_prep.wav', format='wav')

def generate_diarization():  
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token='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')
    DEMO_FILE = {'uri': 'blabla', 'audio': 'input_prep.wav'}
    dz = pipeline(DEMO_FILE)  
    print(type(dz))
    with open("diarization.txt", "w") as text_file:
        text_file.write(str(dz))
    print('done')

def millisec(timeStr):
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s

def group_diarization():
    dzs = open('diarization.txt').read().splitlines()
    groups = []
    g = []
    lastend = 0

    for d in dzs:   
        if g and (g[0].split()[-1] != d.split()[-1]):      #same speaker
            groups.append(g)
            g = []
    
        g.append(d)
    
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
        end = millisec(end)
        if (lastend > end):       #segment engulfed by a previous segment
            groups.append(g)
            g = [] 
        else:
            lastend = end
    if g:
        groups.append(g)

    return groups

def save_groups(groups):
    audio = AudioSegment.from_wav("input_prep.wav")
    for e,g in enumerate(groups):
        print(g)
        start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
        start = millisec(start) #- spacermilli
        end = millisec(end)  #- spacermilli
        print(start, end)
        audio[start:end].export(str(e) + '.wav', format='wav')
        
# prep_file()
# generate_diarization()
dzs = group_diarization()
print(*dzs, sep='\n')
save_groups(dzs)