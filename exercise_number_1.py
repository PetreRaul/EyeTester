import os
import sqlite3
import threading
import math
import cv2
import time
import cvzone
import random
import re

import dashboard
import exercises
import mainmenu
import resources
from cvzone.FaceMeshModule import FaceMeshDetector
from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QTimeLine
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, uic, QtMultimedia
from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QChartView, QBarCategoryAxis
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget, QGraphicsOpacityEffect, QWidget, \
    QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QColor, QFont
import myopia
import statistics
import test
import speech_recognition as sr

widget = None


class ExerciseNumber1(QMainWindow):
    def __init__(self):
        super(ExerciseNumber1, self).__init__()
        loadUi("exercise_number_1.ui", self)

        self.widget = QStackedWidget()

        self.widget.addWidget(self)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

        self.exercise_1_back_button.clicked.connect(self.go_to_dashboard)

        self.widget.setFixedSize(1920, 1000)
        self.widget.move(0, 0)

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.detector = FaceMeshDetector(maxFaces=1)
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

                    colorR = (0, 0, 250)

                    cvzone.putTextRect(img_with_detections, f'Distance: {int(d)}cm',
                                       (face[10][0] - 50, face[10][1] - 50), scale=1,
                                       font=0, thickness=2, colorT=(0, 0, 0), colorR=colorR)

            frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.first_exercise_webcam.setPixmap(QPixmap.fromImage(q_img))

            if cv2.waitKey(1) == ord('q'):
                break

    def go_to_dashboard(self):
        dashboard_button = dashboard.DashboardWindow(connection_data=None)
        print(1)
        self.widget.addWidget(dashboard_button)
        print(2)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

        print(3)

