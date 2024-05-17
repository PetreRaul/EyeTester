import os
import sqlite3
import threading
import cv2
import time
import cvzone
import re
import exercises
import mainmenu
import resources
from cvzone.FaceMeshModule import FaceMeshDetector
from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, uic, QtMultimedia
from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QChartView, QBarCategoryAxis
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget
from PyQt5.QtGui import QPixmap, QImage, QColor
import myopia
import statistics
import test
import speech_recognition as sr

widget = None


# ------------------------MAIN_WINDOW------------------------ #


class DashboardWindow(QMainWindow):
    def __init__(self, connection_data):
        super(DashboardWindow, self).__init__()
        loadUi("dashboard.ui", self)

        self.username = connection_data

        self.icon_widget.setHidden(True)
        self.stackedWidget.setCurrentIndex(1)

        self.start_test_button.clicked.connect(self.go_to_start_test)

        self.homeButton1.clicked.connect(self.go_to_home)
        self.homeButton2.clicked.connect(self.go_to_home)

        self.infoButton1.clicked.connect(self.go_to_statistics)
        self.infoButton2.clicked.connect(self.go_to_statistics)

        self.exercisesButton1.clicked.connect(self.go_to_exercises)
        self.exercisesButton2.clicked.connect(self.go_to_exercises)

        self.statisticsButton1.clicked.connect(self.go_to_information)
        self.statisticsButton2.clicked.connect(self.go_to_information)

        self.signoutButton1.clicked.connect(self.go_to_login)
        self.signoutButton2.clicked.connect(self.go_to_login)

        self.testBotButton.clicked.connect(self.run_myopia)
        self.in_test = False

        self.timer = QTimer(self)

        self.dioptre_distance_left = None  # reper de distanta in functie de dioptrie
        self.dioptre_distance_right = None  # reper de distanta in functie de dioptrie
        self.start_time = None
        self.test_return_value = None  #
        self.widget = widget

        self.is_video_playing = False
        self.is_video_paused = False

        self.is_first_ex_playing = False



        widget.addWidget(self)
        widget.setCurrentIndex(widget.currentIndex() + 1)

        # widget.showFullScreen()
        widget.setFixedSize(1920, 1000)
        widget.move(0, 0)

    def start_webcam(self, dioptre_distance):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        self.timer.start(30)
        self.distance_guidance_label.setText(f'Distance: {int(dioptre_distance)}cm')
        self.green_check = False

        while True:
            success, img = self.capture.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = self.detector.findFaceMesh(img_with_detections, False)
                if faces:
                    face = faces[0]
                    point_left = face[145]
                    point_right = face[374]

                    w, _ = self.detector.findDistance(point_left, point_right)
                    W = 6.3
                    f = 840
                    d = (W * f) / w

                    if dioptre_distance < (int(d) - 10) or dioptre_distance > (int(d) + 10):
                        colorR = (0, 0, 200)
                        colorRGB = (200, 0, 0)
                        self.start_time = None
                        self.green_check = False
                    else:
                        colorR = (0, 200, 0)
                        colorRGB = (0, 150, 30)
                        if not self.green_check:
                            self.start_time = time.time()  # incepere countdown folosing unixtime
                        self.green_check = True

                    cvzone.putTextRect(img_with_detections, f'Distance: {int(d)}cm',
                                       (face[10][0] - 50, face[10][1] - 50), scale=1,
                                       font=0, thickness=2, colorT=(0, 0, 0), colorR=colorR)

                    self.current_distance_label.setText(f'Your distance: {int(d)}cm')
                    self.current_distance_label.setStyleSheet(f'color: rgb{(colorRGB)};')

                    if self.green_check and self.in_test == False:
                        if time.time() - self.start_time > 3:  # verificare 3 secunde consecutive
                            self.in_test = True
                            self.go_to_myopia_test()
                    if self.test_return_value:
                        self.capture.release()
                        return
            frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.Webcam.setPixmap(QPixmap.fromImage(q_img))

            if cv2.waitKey(1) == ord('q'):
                break

    def run_myopia(self):
        letters = myopia.generate_random_letters()
        count_index = 9
        for row in letters:
            for letter in row:
                label_variable = getattr(self, f"label_{count_index}")
                label_variable.setText(letter)

                count_index += 1
        test_menu = test.Test(letters)
        self.test_return_value = test_menu.start_test(6)

    def go_to_login(self):
        if self.is_first_ex_playing is True:
            self.capture_exercise_1.release()
            self.exercise_1.clear()
            self.is_first_ex_playing = False
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        login_button = mainmenu.LoginWindow()
        widget.addWidget(login_button)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.setFixedSize(800, 600)
        widget.move(560, 240)

    def is_float(self):
        try:
            float(self.dioptre_size_left) and float(self.dioptre_size_right)
            return True
        except ValueError:
            return False

    # def dioptre_distance_calculator(self):
    #     dioptre = self.dioptre_size
    #     pixels = self.screen_height
    #     focal_length = 1/float(dioptre)
    #     distance_from_screen = (pixels * focal_length) / (dioptre * pixels)
    #     return distance_from_screen

    def go_to_start_test(self):
        self.dioptre_size_left = self.dioptre_input_left.text()
        self.dioptre_size_right = self.dioptre_input_right.text()
        if len(self.dioptre_size_left) == 0 or len(self.dioptre_size_right) == 0:  # verificare empty space dioptrii
            self.dioptre_error_field.setText("Please insert a dioptre value for both eyes")
        elif not self.is_float():  # verificare tip de date dioptrie
            self.dioptre_error_field.setText("Please insert only float values")
        else:
            # self.dioptre_distance = self.dioptre_distance_calculator()
            self.dioptre_distance_left = abs(float(self.dioptre_size_left)) * 100
            self.dioptre_distance_right = abs(float(self.dioptre_size_right)) * 100
            response = QtWidgets.QMessageBox.question(self, 'Camera permissions', 'Do you want to start your camera?',
                                                      # dialog permisiune camera
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if response == QtWidgets.QMessageBox.Yes:
                capture = cv2.VideoCapture(0)
                if not capture.isOpened():  # verificare camera existenta
                    self.dioptre_error_field.setText("No camera found")
                    capture.release()
                    return False
                capture.release()
                self.stackedWidget.setCurrentIndex(0)
                self.start_webcam(self.dioptre_distance_left)
                print(self.test_return_value)
                test_results = [self.test_return_value]
                if self.test_return_value:
                    self.test_return_value = 0
                    self.in_test = False
                    self.stackedWidget.setCurrentIndex(0)
                    self.start_webcam(self.dioptre_distance_right)
                if self.test_return_value:
                    print(self.test_return_value)
                    test_results.append(self.test_return_value)
                    self.test_return_value = 0
                    self.in_test = False
                    self.add_test_results(test_results)

    def go_to_home(self):
        if self.is_first_ex_playing is True:
            self.capture_exercise_1.release()
            self.exercise_1.clear()
            self.is_first_ex_playing = False
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(1)

    def go_to_information(self):
        if self.is_first_ex_playing is True:
            self.capture_exercise_1.release()
            self.exercise_1.clear()
            self.is_first_ex_playing = False
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(5)
        statistics.Statistics(self)

    def go_to_statistics(self):
        if self.is_first_ex_playing is True:
            self.capture_exercise_1.release()
            self.exercise_1.clear()
            self.is_first_ex_playing = False
        self.stackedWidget.setCurrentIndex(2)
        threading.Thread(target=self.start_exercise_1).start()
        self.stackedWidget_carousel.setCurrentIndex(0)
        self.bottom_button1.setChecked(True)
        self.btn_list = [
            self.bottom_button1,
            self.bottom_button2,
            self.bottom_button3,
            self.previous_button,
            self.next_button
        ]

        for btn in self.btn_list:
            btn.clicked.connect(self.do_change_page)

    def auto_change_page(self):
        current_index = self.stackedWidget_carousel.currentIndex()
        next_index = (current_index + 1) % self.stackedWidget_carousel.count()
        self.stackedWidget_carousel.setCurrentIndex(next_index)
        self.change_background_image(next_index)

    def do_change_page(self):
        button = self.sender()
        current_index = self.stackedWidget_carousel.currentIndex()

        if button == self.next_button:
            if current_index == self.stackedWidget_carousel.count() - 1:
                self.stackedWidget_carousel.setCurrentIndex(0)
            else:
                self.stackedWidget_carousel.setCurrentIndex(current_index + 1)

        elif button == self.previous_button:
            if current_index == 0:
                self.stackedWidget_carousel.setCurrentIndex(self.stackedWidget_carousel.count() - 1)
            else:
                self.stackedWidget_carousel.setCurrentIndex(current_index - 1)

        elif button in self.btn_list:
            index = self.btn_list.index(button)
            self.stackedWidget_carousel.setCurrentIndex(index)

        else:
            pass

        index = self.stackedWidget_carousel.currentIndex()
        self.change_background_image(index)

    def start_exercise_1(self):
        self.is_first_ex_playing = True
        #self.capture_exercise_1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.capture_exercise_1= cv2.VideoCapture(0)
        detector = FaceMeshDetector(maxFaces=1)

        id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        ratio_list = []
        blink_counter = 0
        counter = False
        last_blink = time.time()

        while True:
            success, img = self.capture_exercise_1.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = detector.findFaceMesh(img_with_detections, draw=False)
                current_time = time.time()
                time_since_last_blink = current_time - last_blink
                if faces:
                    face = faces[0]
                    for id in id_list:
                        cv2.circle(img, face[id], 5, (255, 255, 255), cv2.FILLED)

                    left_eye_up_position = face[159]
                    left_eye_down_position = face[23]
                    left_eye_left_position = face[130]
                    left_eye_right_position = face[243]

                    vertical_length, _ = detector.findDistance(left_eye_up_position, left_eye_down_position)
                    horizontal_length, _ = detector.findDistance(left_eye_left_position, left_eye_right_position)

                    # cv2.line(img, left_eye_up_position, left_eye_down_position, (0, 200, 0), 3)
                    # cv2.line(img, left_eye_left_position, left_eye_right_position, (0, 200, 0), 3)

                    ratio = int((vertical_length / horizontal_length) * 100)
                    ratio_list.append(ratio)

                    if len(ratio_list) > 3:
                        ratio_list.pop(0)
                    ratio_average = sum(ratio_list) / len(ratio_list)
                    print(ratio_average)

                    if ratio_average < 35 and counter == 0:
                        blink_counter += 1
                        counter = 1
                        last_blink = current_time
                    if counter != 0:
                        counter += 1
                        if counter > 10:
                            counter = 0

                    print(blink_counter)

                if time_since_last_blink > 5:
                    cvzone.putTextRect(img_with_detections, 'Please blink', (20, 150), scale=1.5, thickness=2, colorR=(255, 0, 0))

            frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.exercise_1.setPixmap(QPixmap.fromImage(q_img))

            if cv2.waitKey(1) == ord('q'):
                break

    def change_background_image(self, index):
        if index == 0:
            self.bottom_button1.setChecked(True)
        elif index == 1:
            self.bottom_button2.setChecked(True)
        else:
            self.bottom_button3.setChecked(True)

    def go_to_exercises(self):
        if self.is_first_ex_playing is True:
            self.capture_exercise_1.release()
            self.exercise_1.clear()
            self.is_first_ex_playing = False
        self.stackedWidget.setCurrentIndex(3)

    def play_pause(self):
        if self.is_video_paused is False and self.is_video_playing is True:
            self.player.pause()
            self.is_video_paused = True
        else:
            self.player.play()
            self.is_video_paused = False
        if self.is_video_playing is False:
            self.player.play()
            self.is_video_playing = True

    def go_to_myopia_test(self):
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(4)
        threading.Thread(target=self.run_myopia).start()

    def add_test_results(self, test_results):

        print(test_results)

        connection = sqlite3.connect("accounts.db")
        cursor = connection.cursor()
        sql = 'INSERT INTO Scores (Username_People, Score_left_first, Score_left_second, Score_right_first, Score_right_second, Timestamp) VALUES (?, ?, ?, ?, ?, ?)'
        timestamp = time.time()

        try:
            cursor.execute(sql, (self.username, test_results[0][0], test_results[0][1], test_results[1][0], test_results[1][1], timestamp))
            connection.commit()
            print("Score and username inserted successfully")

        except Exception as e:
            connection.rollback()
            print("Failed to insert score and username:", str(e))

        connection.close()
