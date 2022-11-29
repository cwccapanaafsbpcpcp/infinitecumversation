from pydub import AudioSegment
from pyannote.audio import Pipeline
import os
import whisper
import json
# Token: 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


#Fuck all this Indian-written shit I stole
def prep_file():
    spacermilli = 2000
    spacer = AudioSegment.silent(duration=spacermilli)
    audio = AudioSegment.from_mp3("input.mp3") 
    audio = spacer.append(audio, crossfade=0)
    audio.export('input_prep.wav', format='wav')

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

# I have the start/ends of when speaker is speaking, ffmpeg needs when they aren't speaking. There's an easier way somehow
def generate_mute_filters(dzs, speaker): 
    dzs = [i for i in dzs if i[0] == speaker]
    filters = ['between(t\,{}\,{})'.format(0,dzs[0][1])]
    for i in range(len(dzs)-1):
        start = dzs[i][2]
        stop = dzs[i+1][1]
        filters.append('between(t\,{}\,{})'.format(start, stop))
    filters.append('between(t\,{}\,{})'.format(dzs[-1][2], 99999)) # :)
    return filters

def generate_file(input_file, dzs, speaker):
    mute_filters = '+'.join(generate_mute_filters(dzs, speaker))
    input_prefix = input_file.rstrip('.wav')
    filtered_filename = f'{input_prefix}_{speaker}.wav'
    ffmpeg_cmd = f'ffmpeg -y -i {input_file} -af volume=0:enable=\'{mute_filters}\' {filtered_filename}'
    os.system(ffmpeg_cmd)
    return filtered_filename

def transcribe(filename):
    model = whisper.load_model('medium.en')
    result = model.transcribe(filename)
    print(result)


def main():
    input_file = 'trim.wav'
    print('loading pipeline')
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token='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')
    print('diarizing')
    diarization = pipeline(input_file)
    dzs = [(i[2], i[0].start, i[0].end) for i in diarization.itertracks(yield_label=True)]
    speakers = set([i[0] for i in dzs])
    dzs = sorted(dzs, key=lambda dz: dz[1])
    for speaker in speakers:
        print(f'filtering {speaker}')
        filtered_audio = generate_file(input_file, dzs, speaker)
        print(f'transcribing {filtered_audio}')
        transcribe(filtered_audio)
   
if __name__ == '__main__':
    main()