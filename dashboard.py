import threading
import cv2
import time
import cvzone
import re
import mainmenu
import resources
from cvzone.FaceMeshModule import FaceMeshDetector
from PyQt5.QtCore import Qt, QTimer
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import *
import myopia
import test

widget = None

# ------------------------MAIN_WINDOW------------------------ #


class DashboardWindow(QMainWindow):
    def __init__(self):
        super(DashboardWindow, self).__init__()
        loadUi("dashboard.ui", self)

        self.icon_widget.setHidden(True)
        self.stackedWidget.setCurrentIndex(1)

        self.start_test_button.clicked.connect(self.go_to_start_test)

        self.homeButton1.clicked.connect(self.go_to_home)
        self.homeButton2.clicked.connect(self.go_to_home)

        self.statisticsButton1.clicked.connect(self.go_to_statistics)
        self.statisticsButton2.clicked.connect(self.go_to_statistics)

        self.exercisesButton1.clicked.connect(self.go_to_exercises)
        self.exercisesButton2.clicked.connect(self.go_to_exercises)

        self.signoutButton1.clicked.connect(self.go_to_login)
        self.signoutButton2.clicked.connect(self.go_to_login)

        self.testBotButton.clicked.connect(self.run_myopia)
        self.in_test = False


        self.timer = QTimer(self)

        self.dioptre_distance = None  # reper de distanta in functie de dioptrie
        self.start_time = None


        widget.addWidget(self)
        widget.setCurrentIndex(widget.currentIndex() + 1)

        # widget.showFullScreen()
        widget.setFixedSize(1920, 1000)
        widget.move(0, 0)

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        #self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        self.timer.start(30)
        dioptre_distance = self.dioptre_distance
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
                            self.start_time = time.time() # incepere countdown folosing unixtime
                        self.green_check = True


                    cvzone.putTextRect(img_with_detections, f'Distance: {int(d)}cm', (face[10][0] - 50, face[10][1] - 50), scale=1,
                            font=0, thickness=2, colorT=(0, 0, 0), colorR= colorR)

                    self.current_distance_label.setText(f'Your distance: {int(d)}cm')
                    self.current_distance_label.setStyleSheet(f'color: rgb{(colorRGB)};')

                    if self.green_check and self.in_test == False:
                        if time.time() - self.start_time > 3: # verificare 3 secunde consecutive
                            self.in_test = True
                            self.go_to_myopia_test()





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
        test_menu.start_test()


    def go_to_login(self):
        login_button = mainmenu.LoginWindow()
        widget.addWidget(login_button)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(800, 600)
        widget.move(560, 240)

    def is_float(self):
        try:
            float(self.dioptre_size)
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
        self.dioptre_size = self.dioptre_input.text()
        if len(self.dioptre_size) == 0: # verificare empty space dioptrie
            self.dioptre_error_field.setText("Please insert a dioptre value")
        elif not self.is_float(): # verificare tip de date dioptrie
            self.dioptre_error_field.setText("Value is wrong. Insert a float value")
        else:
            # self.dioptre_distance = self.dioptre_distance_calculator()
            self.dioptre_distance = abs(float(self.dioptre_size)) * 100
            response = QtWidgets.QMessageBox.question(self, 'Camera permissions', 'Do you want to start your camera?', # dialog permisiune camera
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if response == QtWidgets.QMessageBox.Yes:
                capture = cv2.VideoCapture(0)
                if not capture.isOpened(): # verificare camera existenta
                    self.dioptre_error_field.setText("No camera found")
                    capture.release()
                    return False
                capture.release()
                self.stackedWidget.setCurrentIndex(0)
                self.start_webcam()

    def go_to_home(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_statistics(self):
        self.stackedWidget.setCurrentIndex(2)

    def go_to_exercises(self):
        self.stackedWidget.setCurrentIndex(3)

    def go_to_myopia_test(self):
        self.stackedWidget.setCurrentIndex(4)
        threading.Thread(target=self.run_myopia).start()
