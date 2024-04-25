import random
import speech_recognition as sr
import time
import os
import playsound
from gtts import gTTS
from time import ctime

recognizer = sr.Recognizer()

def generate_random_letters():
        letters = []
        for i in range(7):
            row = ''.join(random.choices('CDEFLOPTZ', k=i+2))
            letters.append(row)
        letters.append(''.join(random.choices('CDEFLOPTZ', k=8)))
        letters.append(''.join(random.choices('CDEFLOPTZ', k=8)))
        letters.append(''.join(random.choices('CDEFLOPTZ', k=9)))
        return letters

