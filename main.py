from pydub import AudioSegment
from pyannote.audio import Pipeline
from datetime import datetime
import re
import whisper
# Token: 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


#Fuck all this Indian-written shit I stole
# def prep_file():
#     spacermilli = 2000
#     spacer = AudioSegment.silent(duration=spacermilli)
#     audio = AudioSegment.from_mp3("input.mp3") 
#     audio = spacer.append(audio, crossfade=0)
#     audio.export('input_prep.wav', format='wav')

# def generate_diarization():  
#     pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token='')
#     DEMO_FILE = {'uri': 'blabla', 'audio': 'input_prep.wav'}
#     dz = pipeline(DEMO_FILE)  
#     with open("diarization.txt", "w") as text_file:
#         text_file.write(str(dz))

# def millisec(timeStr):
#   spl = timeStr.split(":")
#   s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
#   return s

# def group_diarization():
#     dzs = open('diarization.txt').read().splitlines()
#     groups = []
#     g = []
#     lastend = 0

#     for d in dzs:   
#         if g and (g[0].split()[-1] != d.split()[-1]):      #same speaker
#             groups.append(g)
#             g = []
    
#         g.append(d)
    
#         end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
#         end = millisec(end)
#         if (lastend > end):       #segment engulfed by a previous segment
#             groups.append(g)
#             g = [] 
#         else:
#             lastend = end
#     if g:
#         groups.append(g)

#     return groups

# def save_groups(groups):
#     audio = AudioSegment.from_wav("input_prep.wav")
#     for e,g in enumerate(groups):
#         spt = g[0].split(' ')
#         st = datetime.strptime(spt[1], '%H:%M:%S.%f')
#         et = datetime.strptime(spt[1], '%H:%M:%S.%f]')
#         print(st)
#         segment, speaker = g[0].split(' ')[-2:]
#         start_ts = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
#         end_ts = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
#         start_ts = millisec(start_ts)
#         end_ts = millisec(end_ts)
#         audio[start_ts:end_ts].export(str(e) + '.wav', format='wav')
# prep_file()
# generate_diarization()
# dzs = group_diarization()
# save_groups(dzs)

def mute_filter(start, stop):
    return "volume=enable='between(t,{},{})':volume=0".format(start, stop)

def main():
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token='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')
    model = whisper.load_model('tiny.en')
    diarization = pipeline('input_prep.wav')
    dzs = [(i[2], i[0].start, i[0].end) for i in diarization.itertracks(yield_label=True)]
    speakers = set([i[0] for i in dzs])
    x = sorted(dzs, key=lambda dz: dz[1])
    print(speakers)
    
if __name__ == '__main__':
    main()