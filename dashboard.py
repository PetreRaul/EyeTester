import os
import sqlite3
import threading
import math
import cv2
import time
import cvzone
import random
import re
import exercise_number_1
import exercises
import mainmenu
import resources
from cvzone.FaceMeshModule import FaceMeshDetector
from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QTimeLine
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, uic, QtMultimedia
from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QChartView, QBarCategoryAxis
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget, QGraphicsOpacityEffect, QWidget, \
    QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QColor, QFont
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

        self.nutritionButton1.clicked.connect(self.go_to_nutrition)
        self.nutritionButton2.clicked.connect(self.go_to_nutrition)

        self.export_button.clicked.connect(self.go_to_export)

        self.signoutButton1.clicked.connect(self.go_to_login)
        self.signoutButton2.clicked.connect(self.go_to_login)


        self.second_exercise_button.clicked.connect(self.go_to_second_exercise)
        self.third_exercise_button.clicked.connect(self.go_to_third_exercise)

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
        self.timer_group_exercise = None


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
                        colorR = (0, 0, 250)
                        colorRGB = (250, 0, 0)
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
        # if self.is_first_ex_playing is True:
        #     self.capture_exercise_2.release()
        #     self.exercise_2.clear()
        #     self.is_first_ex_playing = False
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
        # if self.is_first_ex_playing is True:
        #     self.capture_exercise_2.release()
        #     self.exercise_2.clear()
        #     self.is_first_ex_playing = False
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(1)

    def go_to_information(self):
        # if self.is_first_ex_playing is True:
        #     self.capture_exercise_2.release()
        #     self.exercise_2.clear()
        #     self.is_first_ex_playing = False
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(5)
        statistics.Statistics(self, None)

    def go_to_nutrition(self):
        # if self.is_first_ex_playing is True:
        #     self.capture_exercise_2.release()
        #     self.exercise_2.clear()
        #     self.is_first_ex_playing = False
        if self.is_video_playing is True:
            self.player.stop()
            self.is_video_playing = False
        self.stackedWidget.setCurrentIndex(6)

    def go_to_export(self):
        file_filter = 'Excel File (.xlsx .xls)'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Select a data file',
            directory='Statistics.xlsx',
            filter=file_filter,
            initialFilter='Excel File (.xlsx *.xls)'
        )
        if response[0]:
            print(response[0])
            statistics.Statistics(self, response[0])

    def go_to_statistics(self):
        # if self.is_first_ex_playing is True:
        #     self.capture_exercise_2.release()
        #     self.exercise_2.clear()
        #     self.is_first_ex_playing = False
        self.stackedWidget.setCurrentIndex(2)
        # threading.Thread(target=self.start_exercise_2).start()
        self.stackedWidget_carousel.setCurrentIndex(0)
        self.bottom_button1.setChecked(True)
        self.btn_list = [
            self.bottom_button1,
            self.bottom_button2,
            self.bottom_button3,
            self.bottom_button4,
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

        if button in self.btn_list:
            index = self.btn_list.index(button)
            self.stackedWidget_carousel.setCurrentIndex(index)

        else:
            pass

        index = self.stackedWidget_carousel.currentIndex()
        self.change_background_image(index)

    # def start_exercise_2(self):
    #     self.is_first_ex_playing = True
    #     self.capture_exercise_2 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    #     #self.capture_exercise_2= cv2.VideoCapture(0)
    #     detector = FaceMeshDetector(maxFaces=1)
    #
    #     id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
    #     ratio_list = []
    #     blink_counter = 0
    #     counter = False
    #     last_blink = time.time()
    #
    #     while True:
    #         success, img = self.capture_exercise_2.read()
    #         if success:
    #             img_with_detections = img.copy()
    #             img_with_detections, faces = detector.findFaceMesh(img_with_detections, draw=False)
    #             current_time = time.time()
    #             time_since_last_blink = current_time - last_blink
    #             if faces:
    #                 face = faces[0]
    #                 for id in id_list:
    #                     cv2.circle(img, face[id], 5, (255, 255, 255), cv2.FILLED)
    #
    #                 left_eye_up_position = face[159]
    #                 left_eye_down_position = face[23]
    #                 left_eye_left_position = face[130]
    #                 left_eye_right_position = face[243]
    #
    #                 vertical_length, _ = detector.findDistance(left_eye_up_position, left_eye_down_position)
    #                 horizontal_length, _ = detector.findDistance(left_eye_left_position, left_eye_right_position)
    #
    #                 # cv2.line(img, left_eye_up_position, left_eye_down_position, (0, 200, 0), 3)
    #                 # cv2.line(img, left_eye_left_position, left_eye_right_position, (0, 200, 0), 3)
    #
    #                 ratio = int((vertical_length / horizontal_length) * 100)
    #                 ratio_list.append(ratio)
    #
    #                 if len(ratio_list) > 3:
    #                     ratio_list.pop(0)
    #                 ratio_average = sum(ratio_list) / len(ratio_list)
    #                 print(ratio_average)
    #
    #                 if ratio_average < 35 and counter == 0:
    #                     blink_counter += 1
    #                     counter = 1
    #                     last_blink = current_time
    #                 if counter != 0:
    #                     counter += 1
    #                     if counter > 10:
    #                         counter = 0
    #
    #                 print(blink_counter)
    #
    #             if time_since_last_blink > 5:
    #                 cvzone.putTextRect(img_with_detections, 'Please blink', (20, 150), scale=1.5, thickness=2, colorR=(255, 0, 0))
    #
    #         frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
    #         h, w, ch = frame.shape
    #         bytes_per_line = ch * w
    #         q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #         self.exercise_2.setPixmap(QPixmap.fromImage(q_img))
    #
    #         if cv2.waitKey(1) == ord('q'):
    #             break

    def change_background_image(self, index):
        if index == 0:
            self.bottom_button1.setChecked(True)
        elif index == 1:
            if self.is_first_ex_playing is True:
                self.capture.release()
                self.is_first_ex_playing = False
            self.camera_holder = self.first_exercise_webcam
            self.exercise_index = 1
            self.exercise_webcam()
            self.bottom_button2.setChecked(True)
        elif index == 2:
            if self.is_first_ex_playing is True:
                self.capture.release()
                self.is_first_ex_playing = False
            self.camera_holder = self.second_exercise_webcam
            self.exercise_index = 2
            self.exercise_webcam()
            self.bottom_button3.setChecked(True)
        else:
            if self.is_first_ex_playing is True:
                self.capture.release()
                self.is_first_ex_playing = False
            self.camera_holder = self.third_exercise_webcam
            self.exercise_index = 3
            self.exercise_webcam()
            self.bottom_button4.setChecked(True)

    def go_to_exercises(self):
        # if self.is_first_ex_playing is True:
        #     self.capture_exercise_2.release()
        #     self.exercise_2.clear()
        #     self.is_first_ex_playing = False
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

    def go_to_second_exercise(self):
        second_exercise = ExerciseNumber2(widget.currentIndex())
        widget.addWidget(second_exercise)
        widget.setCurrentIndex(widget.count() - 1)
        second_exercise.start_webcam_second_exercise()

    def go_to_third_exercise(self):
        third_exercise = ExerciseNumber3(widget.currentIndex())
        widget.addWidget(third_exercise)
        widget.setCurrentIndex(widget.count() - 1)
        third_exercise.start_webcam_third_exercise()

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

    def go_to_dashboard(self):
        dashboard = DashboardWindow(self)
        widget.addWidget(dashboard)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.setFixedSize(1920, 1000)
        widget.move(0, 0)

    def go_to_first_exercise(self):
        first_exercise = ExerciseNumber1(widget.currentIndex())
        widget.addWidget(first_exercise)
        widget.setCurrentIndex(widget.count() - 1)
        first_exercise.start_webcam_first_exercise()


    def exercise_webcam(self):
        print("EXEECEIIEWEBXCAM")
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.detector = FaceMeshDetector(maxFaces=1)
        self.is_first_ex_playing = True
        dioptre_distance = 30
        self.green_check = False
        self.in_test = False

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
                        colorR = (0, 0, 250)
                        colorRGB = (250, 0, 0)
                        self.start_time = None
                        self.green_check = False
                    else:
                        colorR = (0, 200, 0)
                        colorRGB = (0, 150, 30)
                        if not self.green_check:
                            self.start_time = time.time()
                        self.green_check = True

                    cvzone.putTextRect(img_with_detections, f'Distance: {int(d)}cm',
                                       (face[10][0] - 50, face[10][1] - 50), scale=1,
                                       font=0, thickness=2, colorT=(0, 0, 0), colorR=colorR)

                    self.current_distance_label.setText(f'Your distance: {int(d)}cm')
                    self.current_distance_label.setStyleSheet(f'color: rgb{(colorRGB)};')

                    if self.green_check and self.in_test == False:
                        if time.time() - self.start_time > 3:  # verificare 3 secunde consecutive
                            self.in_test = True
                            #self.capture.release()
                            #self.camera_holder.clear()

                            self.green_check = False
                            if self.exercise_index == 1:
                                self.go_to_first_exercise()
                            elif self.exercise_index == 2:
                                self.go_to_second_exercise()
                            else:
                                self.go_to_third_exercise()


            frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_holder.setPixmap(QPixmap.fromImage(q_img))

            if cv2.waitKey(1) == ord('q'):
                break


######################## EXERCISE 1 #######################################


class ExerciseNumber1(QMainWindow):
    def __init__(self, main_window_index):
        super(ExerciseNumber1, self).__init__()
        loadUi("exercise_number_1.ui", self)

        self.widget = QStackedWidget()

        self.main_window_index = main_window_index
        print(main_window_index)

        self.widget.addWidget(self)

        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        self.circle_slider.valueChanged.connect(self.number_changed)
        self.circle_slider.setValue(1)

        self.exercise_1_back_button.clicked.connect(self.stop)


        self.widget.setFixedSize(1920, 1000)
        self.widget.move(0, 0)

    def start_webcam_first_exercise(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        ratio_list = []
        blink_counter = 0
        counter = False
        last_blink = time.time()
        dioptre_distance = 30

        while True:
            success, img = self.capture.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = self.detector.findFaceMesh(img_with_detections, False)
                current_time = time.time()
                time_since_last_blink = current_time - last_blink
                if faces:
                    face = faces[0]
                    point_left = face[145]
                    point_right = face[374]

                    w, _ = self.detector.findDistance(point_left, point_right)
                    W = 6.3
                    f = 840
                    d = (W * f) / w

                    if dioptre_distance < (int(d) - 10) or dioptre_distance > (int(d) + 10):
                        colorRGB = (250, 0, 0)
                    else:
                        colorRGB = (0, 150, 30)

                    self.current_distance_label_first.setText(f'Your distance: {int(d)}cm')
                    self.current_distance_label_first.setStyleSheet(f'color: rgb{(colorRGB)};')


                    ######################### BLINKING #########################

                    for id in id_list:
                        cv2.circle(img, face[id], 5, (255, 255, 255), cv2.FILLED)

                    left_eye_up_position = face[159]
                    left_eye_down_position = face[23]
                    left_eye_left_position = face[130]
                    left_eye_right_position = face[243]

                    vertical_length, _ = self.detector.findDistance(left_eye_up_position, left_eye_down_position)
                    horizontal_length, _ = self.detector.findDistance(left_eye_left_position, left_eye_right_position)

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

                if time_since_last_blink > 5:
                    self.blink_label_1.setText(f'Please Blink')
                elif time_since_last_blink < 5:
                    self.blink_label_1.setText("")

            if cv2.waitKey(1) == ord('q'):
                break

    def stop(self):
        self.capture.release()
        widget.setCurrentIndex(self.main_window_index)
        return 1

    def number_changed(self):
        new_value = self.circle_slider.value()
        font = QFont("Arial", new_value * 40)
        self.circle_label.setFont(font)
        self.circle_label.setText("⊙")


class ExerciseNumber2(QMainWindow):
    def __init__(self, main_window_index):
        super(ExerciseNumber2, self).__init__()
        loadUi("exercise_number_2.ui", self)

        self.widget = QStackedWidget()

        self.main_window_index = main_window_index

        self.widget.addWidget(self)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

        self.exercise_2_back_button.clicked.connect(self.stop)

        self.widget.setFixedSize(1920, 1000)
        self.widget.move(0, 0)

        self.group_1.setVisible(True)
        self.group_2.setVisible(False)
        self.group_3.setVisible(False)
        self.group_4.setVisible(False)
        self.group_5.setVisible(False)
        self.timer_group_exercise = QTimer()
        self.timer_group_exercise.timeout.connect(self.toggle_groups)
        self.timer_group_exercise.start(1000)

    def start_webcam_second_exercise(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        ratio_list = []
        blink_counter = 0
        counter = False
        last_blink = time.time()
        dioptre_distance = 30

        while True:
            success, img = self.capture.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = self.detector.findFaceMesh(img_with_detections, False)
                current_time = time.time()
                time_since_last_blink = current_time - last_blink
                if faces:
                    face = faces[0]
                    point_left = face[145]
                    point_right = face[374]

                    w, _ = self.detector.findDistance(point_left, point_right)
                    W = 6.3
                    f = 840
                    d = (W * f) / w

                    if dioptre_distance < (int(d) - 10) or dioptre_distance > (int(d) + 10):
                        colorRGB = (250, 0, 0)
                    else:
                        colorRGB = (0, 150, 30)

                    self.current_distance_label_second.setText(f'Your distance: {int(d)}cm')
                    self.current_distance_label_second.setStyleSheet(f'color: rgb{(colorRGB)};')


                    ######################### BLINKING #########################

                    for id in id_list:
                        cv2.circle(img, face[id], 5, (255, 255, 255), cv2.FILLED)

                    left_eye_up_position = face[159]
                    left_eye_down_position = face[23]
                    left_eye_left_position = face[130]
                    left_eye_right_position = face[243]

                    vertical_length, _ = self.detector.findDistance(left_eye_up_position, left_eye_down_position)
                    horizontal_length, _ = self.detector.findDistance(left_eye_left_position, left_eye_right_position)

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

                if time_since_last_blink > 5:
                    self.blink_label_2.setText(f'Please Blink')
                elif time_since_last_blink < 5:
                    self.blink_label_2.setText("")

            if cv2.waitKey(1) == ord('q'):
                break

    def stop(self):
        widget.setCurrentIndex(self.main_window_index)
        return

    def toggle_groups(self):
        total_groups = [self.group_1, self.group_2, self.group_3, self.group_4, self.group_5]
        for group in total_groups:
            group.setVisible(False)
        random.choice(total_groups).setVisible(True)


class ExerciseNumber3(QMainWindow):
    def __init__(self, main_window_index):
        super(ExerciseNumber3, self).__init__()
        loadUi("exercise_number_3.ui", self)

        self.widget = QStackedWidget()

        self.main_window_index = main_window_index
        print(main_window_index)

        self.widget.addWidget(self)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

        self.exercise_3_back_button.clicked.connect(self.stop)

        self.widget.setFixedSize(1920, 1000)
        self.widget.move(0, 0)

        self.center_x = 1030
        self.center_y = 355
        self.radius = 330  # Raza cercului
        self.angle = 100

        if hasattr(self, 'timeline') and self.timeline.state() == QTimeLine.Running:
            self.timeline.stop()

        self.timeline = QTimeLine(4500, self)
        self.timeline.setFrameRange(0, 360)
        self.timeline.frameChanged.connect(self.update_position)
        self.timeline.setCurveShape(QTimeLine.EaseInOutCurve)
        self.timeline.finished.connect(self.restart_animation)
        self.timeline.start()

    def start_webcam_third_exercise(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        ratio_list = []
        blink_counter = 0
        counter = False
        last_blink = time.time()
        dioptre_distance = 30

        while True:
            success, img = self.capture.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = self.detector.findFaceMesh(img_with_detections, False)
                current_time = time.time()
                time_since_last_blink = current_time - last_blink
                if faces:
                    face = faces[0]
                    point_left = face[145]
                    point_right = face[374]

                    w, _ = self.detector.findDistance(point_left, point_right)
                    W = 6.3
                    f = 840
                    d = (W * f) / w

                    if dioptre_distance < (int(d) - 10) or dioptre_distance > (int(d) + 10):
                        colorRGB = (250, 0, 0)
                    else:
                        colorRGB = (0, 150, 30)

                    self.current_distance_label_third.setText(f'Your distance: {int(d)}cm')
                    self.current_distance_label_third.setStyleSheet(f'color: rgb{(colorRGB)};')


                    ######################### BLINKING #########################

                    for id in id_list:
                        cv2.circle(img, face[id], 5, (255, 255, 255), cv2.FILLED)

                    left_eye_up_position = face[159]
                    left_eye_down_position = face[23]
                    left_eye_left_position = face[130]
                    left_eye_right_position = face[243]

                    vertical_length, _ = self.detector.findDistance(left_eye_up_position, left_eye_down_position)
                    horizontal_length, _ = self.detector.findDistance(left_eye_left_position, left_eye_right_position)

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

                if time_since_last_blink > 5:
                    self.blink_label_3.setText(f'Please Blink')
                elif time_since_last_blink < 5:
                    self.blink_label_3.setText("")

            if cv2.waitKey(1) == ord('q'):
                break
    def update_position(self, angle):
        x = self.center_x + self.radius * math.cos(math.radians(angle))
        y = self.center_y + self.radius * math.sin(math.radians(angle))

        self.exercise_1234.move(int(x), int(y))

    def restart_animation(self):
        self.timeline.setCurrentTime(0)
        self.timeline.start()

    def stop(self):
        widget.setCurrentIndex(self.main_window_index)
        return
