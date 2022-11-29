from pydub import AudioSegment
from pyannote.audio import Pipeline
import os
import whisper
import json
# Token: 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




def prep_file(input_filename):
    audio = AudioSegment.from_mp3(input_filename) 
    output_filename = input_filename.replace('.mp3', '.wav')
    audio.export(output_filename, format='wav')
    return output_filename


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
    with open('filter.txt', 'w') as f:
        f.write(f'volume=0:enable=\'{mute_filters}\'') # required on windows due to command line char limit
    ffmpeg_cmd = f'ffmpeg -y -i {input_file} -filter_script:a filter.txt {filtered_filename}'
    os.system(ffmpeg_cmd)
    return filtered_filename

def transcribe(filename):
    out_file = filename.rstrip('.wav') + '.json'
    model = whisper.load_model('base.en')
    result = model.transcribe(filename)
    
    with open(out_file, 'w') as f:
        json.dump(result, f)


def main():
    input_file = prep_file('input.mp3')
    print('loading pipeline')
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token='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')
    print('diarizing')
    diarization = pipeline(input_file)
    dzs = [(i[2], i[0].start, i[0].end) for i in diarization.itertracks(yield_label=True)]
    speakers = set([i[0] for i in dzs])
    print(f'found {len(speakers)} speakers')
    dzs = sorted(dzs, key=lambda dz: dz[1])
    for speaker in speakers:
        print(f'filtering {speaker}')
        filtered_audio = generate_file(input_file, dzs, speaker)
        print(f'transcribing {filtered_audio}')
        transcribe(filtered_audio)
   
if __name__ == '__main__':
    main()