import pyttsx3
import speech_recognition as sr
import threading
import dashboard

engine = pyttsx3.init()
recognizer = sr.Recognizer()


class Test:

    def __init__(self, letters):
        self.letters = letters
        self.correct_answers = 0
        self.in_test = True
        self.given_answers = 0
        self.test_state = 0
        self.last_row_results = None

    def speak_letters(self, row, column):
        position = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth"]
        engine.say(f"Please read the {position[column]} letter on the row {row}")
        threading.Thread(target=engine.runAndWait).start()  # porneste un proces separat pentru functia de vorbire

    def recognize_speech(self):
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language='ro-RO').upper()
                print(text)
                return text
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                return None
            except sr.RequestError:
                print("Sorry, there was an issue with the service.")
                return None

    def check_letter(self, input_string, row, column):
        words = input_string.split()
        if len(words) >= 3:
            letter = words[2]
            if letter.isalpha():
                self.given_answers += 1
                if self.letters[row][column] == letter:
                    return True
                else:
                    return False

    def check_results(self, row):
        if self.correct_answers >= len(self.letters[row]) / 2 + 1:
            if self.test_state == 0:
                engine.say(f"Correct! Now we are moving on line {row + 3}")
                self.test_state = 1
                self.start_test(row + 1)
            elif self.test_state == 1:
                self.last_row_results = 1
                engine.say(f"Correct! Your vision is good!")
            elif self.test_state == -1:
                self.last_row_results = 1
                engine.say(f"Correct! Your vision is alright, but you need eye exercises!")

        else:
            if self.test_state == 0:
                engine.say(f"Wrong! Now we are moving on line {row + 1}")
                self.test_state = -1
                self.start_test(row - 1)
            elif self.test_state == 1:
                self.last_row_results = -1
                engine.say(f"Wrong! Your vision is alright, but you need eye exercises!")
            elif self.test_state == -1:
                self.last_row_results = -1
                engine.say(f"Wrong! Check an eye specialist!")

        engine.runAndWait()
        if self.test_state != 0:
            return [self.test_state, self.last_row_results]

    def start_test(self, row):

        self.correct_answers = 0
        self.given_answers = 0
        real_rows = row + 2
        column = 0

        while self.in_test:
            print(column)
            if ((self.correct_answers >= len(self.letters[row]) / 6 + 1) or
                    (self.given_answers == len(self.letters[row])) or
                    (self.given_answers - self.correct_answers >= len(self.letters[row]) / 2)):
                return self.check_results(row)
            print("while loop")
            self.speak_letters(real_rows, column)
            letter = self.recognize_speech()
            if letter is None:
                self.speak_letters(real_rows, column)
                letter = self.recognize_speech()
            if letter is None:
                print("crestere coloana")
                if column + 1 == len(self.letters[row]):
                    column = 0
                else:
                    column += 1
            else:
                if self.check_letter(letter, row, column):
                    self.correct_answers += 1

                column += 1
                print(self.correct_answers)
