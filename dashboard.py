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
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget
from PyQt5.QtGui import QPixmap, QImage
import myopia
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

                    # cv2.line(img_with_detections, point_left, point_right, (0, 200, 0), 3)
                    # cv2.circle(img_with_detections, point_left, 5, (255, 0, 255), cv2.FILLED)
                    # cv2.circle(img_with_detections, point_right, 5, (255, 0, 255), cv2.FILLED)

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
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(1)

    def go_to_information(self):
        self.stackedWidget.setCurrentIndex(5)

    def go_to_statistics(self):
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(2)

        self.widget.setStyleSheet("#widget {background-image: url(:/newPrefix/ex5.webp);}")

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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_change_page)
        self.timer.start(10000)  # setare interval schimbare imagine

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

        self.timer.stop()
        self.timer.start(10000)

        index = self.stackedWidget_carousel.currentIndex()
        self.change_background_image(index)

    def change_background_image(self, index):
        if index == 0:
            self.widget.setStyleSheet("#widget {background-image: url(:/newPrefix/ex5.webp);}")
            self.bottom_button1.setChecked(True)
        elif index == 1:
            self.widget.setStyleSheet("#widget {background-image: url(:/newPrefix/ex3.png);}")
            self.bottom_button2.setChecked(True)
        else:
            self.widget.setStyleSheet("#widget {background-image: url(:/newPrefix/ex4.png);}")
            self.bottom_button3.setChecked(True)

    def go_to_exercises(self):
        self.stackedWidget.setCurrentIndex(3)
        self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        file = os.path.join(os.path.dirname(__file__), "myvideo.mp4")
        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(file)))
        self.player.setVideoOutput(self.video_player)
        self.play_pause_button.clicked.connect(self.play_pause)

        self.video_position.sliderMoved.connect(self.set_position)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

        self.player.play()

        self.is_video_playing = True

    def position_changed(self, position):
        self.video_position.setValue(position)

    def duration_changed(self, duration):
        self.video_position.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)

    def play_pause(self):
        if self.is_video_paused is False and self.is_video_playing is True:
            self.player.pause()
            self.is_video_paused = True
        else:
            self.player.play()
            self.is_video_paused = False

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
