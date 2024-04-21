import random
import speech_recognition as sr
import time
import os
import playsound
from gtts import gTTS
from time import ctime

r = sr.Recognizer()

def record_audio(ask=False):
    with sr.Microphone() as source:
        if ask:
            myopia_speak(ask)
        audio = r.listen(source)
        voice_data= ''
        try:
            voice_data = r.recognize_google(audio)
        except sr.UnknownValueError:
            myopia_speak('Sorry I did not understand')
        except sr.RequestError:
            myopia_speak('Sorry, my speech service is down')
        return voice_data

def myopia_speak(audio_string):
    tts = gTTS(text=audio_string, lang='en')
    # Generate a random number for creating a unique filename
    r = random.randint(1, 10000000)
    audio_file = 'audio' + str(r) + '.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    print(audio_string)
    os.remove(audio_file)

def respond(voice_data, text_to_read=None):
    if 'what is your name' in voice_data:
        myopia_speak('My name is Myopia bot')

    if 'what is the time' in voice_data:
        myopia_speak('The time is ' + ctime())

    if 'close the application' in voice_data:
        exit()
    if 'read letters' in voice_data:
        if text_to_read:
            myopia_speak(text_to_read)
        else:
            rows = 2  # Adjust as needed
            columns = 5  # Adjust as needed
            letters = generate_random_letters(rows, columns)
            for row in letters:
                for letter in row:
                    myopia_speak(letter)

def generate_random_letters():
        letters = []
        for i in range(7):
            row = ''.join(random.choices('CDEFLOPTZ', k=i+2))
            letters.append(row)
        letters.append(''.join(random.choices('CDEFLOPTZ', k=8)))
        letters.append(''.join(random.choices('CDEFLOPTZ', k=8)))
        letters.append(''.join(random.choices('CDEFLOPTZ', k=9)))
        return letters


def main():
    time.sleep(1)
    myopia_speak('How can I help you')
    while(1):
        voicedata = record_audio()
        respond(voicedata)

# if __name__ == "__main__":
#     main()