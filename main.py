import sqlite3
import sys
import cv2
import resources
from cvzone.FaceMeshModule import FaceMeshDetector
from PyQt5.QtCore import Qt, QTimer
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import *
import myopia


class DashboardWindow(QMainWindow):
    def __init__(self):
        super(DashboardWindow, self).__init__()
        loadUi("dashboard.ui", self)

        self.icon_widget.setHidden(True)

        self.homeButton1.clicked.connect(self.go_to_home)
        self.homeButton2.clicked.connect(self.go_to_home)

        self.statisticsButton1.clicked.connect(self.go_to_statistics)
        self.statisticsButton2.clicked.connect(self.go_to_statistics)

        self.exercisesButton1.clicked.connect(self.go_to_exercises)
        self.exercisesButton2.clicked.connect(self.go_to_exercises)

        self.signoutButton1.clicked.connect(self.go_to_login)
        self.signoutButton2.clicked.connect(self.go_to_login)

        self.testBotButton.clicked.connect(self.run_myopia)
        self.testBotVideoButton.clicked.connect(self.start_webcam)

        self.timer = QTimer(self)

        # self.timer.timeout.connect(self.update_frame)
        # self.capture = None

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        self.timer.start(30)

        while True:
            success, img = self.capture.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = self.detector.findFaceMesh(img_with_detections, False)

                if faces:
                    face = faces[0]
                    point_left = face[145]
                    point_right = face[374]

                    cv2.line(img_with_detections, point_left, point_right, (0, 200, 0), 3)
                    cv2.circle(img_with_detections, point_left, 5, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img_with_detections, point_right, 5, (255, 0, 255), cv2.FILLED)

                    w, _ = self.detector.findDistance(point_left, point_right)
                    print(w)
                    W = 6.3
                    f = 840
                    d = (W * f) / w
                    print(d)

                frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.Webcam.setPixmap(QPixmap.fromImage(q_img))

            if cv2.waitKey(1) == ord('q'):
                break

    def run_myopia(self):
        letters = myopia.generate_random_letters(rows=2, columns=5)
        letters_text = '\n'.join([' '.join(row) for row in letters])
        self.visibleLetter1.setText(letters_text)
        response = QtWidgets.QMessageBox.question(self, 'Speak Letters', 'Do you want Myopia to speak the letters?',
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if response == QtWidgets.QMessageBox.Yes:
            myopia.respond('read letters', letters_text)

    def go_to_login(self):
        login_button = LoginWindow()
        widget.addWidget(login_button)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_home(self):
        self.stackedWidget.setCurrentIndex(0)

    def go_to_statistics(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_exercises(self):
        self.stackedWidget.setCurrentIndex(2)

# ------------------------MAIN_WINDOW------------------------ #


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainwindow.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.loginButton.clicked.connect(self.go_to_login)
        self.registerButton.clicked.connect(self.go_to_register)
        self.setFixedSize(709, 599)

    def go_to_login(self):
        login_button = LoginWindow()
        widget.addWidget(login_button)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_register(self):
        register_button = RegisterWindow()
        widget.addWidget(register_button)
        widget.setCurrentIndex(widget.currentIndex()+1)


# ------------------------REGISTER_WINDOW------------------------ #
class RegisterWindow(QDialog):
    def __init__(self):
        super(RegisterWindow, self).__init__()
        loadUi("register.ui", self)
        self.passwordFieldRegister.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordFieldConfirmPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.createAccountButton.clicked.connect(self.signup_function)

        self.backRegisterButton.clicked.connect(self.go_to_main_window)

    def signup_function(self):
        username = self.userFieldRegister.text()
        password = self.passwordFieldRegister.text()
        password_confirm = self.passwordFieldConfirmPassword.text()

        if len(username) == 0 or len(password) == 0 or len(password_confirm) == 0:
            self.errorRegister.setText("Please complete all fields")

        elif password != password_confirm:
            self.errorRegister.setText("Passwords do not match.")

        else:
            connection = sqlite3.connect("accounts.db")
            cursor = connection.cursor()
            user_info = [username, password]
            cursor.execute('INSERT INTO People (Username, Password) VALUES (?,?)', user_info)
            connection.commit()
            print("Successfully registered the user")
            self.go_to_main_window()

    def go_to_main_window(self):
        backregister_button = MainWindow()
        widget.addWidget(backregister_button)
        widget.setCurrentIndex(widget.currentIndex()+1)

# ------------------------LOGIN_WINDOW------------------------ #


class LoginWindow(QDialog):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi("login.ui", self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.loginAccount.clicked.connect(self.login_function)
        self.backLoginButton.clicked.connect(self.go_to_main_window)
        self.setFixedSize(709, 599)

    def go_to_main_window(self):
        backlogin_button = MainWindow()
        widget.addWidget(backlogin_button)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_dashboard_window(self):
        login_button = DashboardWindow()
        widget.addWidget(login_button)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login_function(self):
        username = self.userField.text()
        password = self.passwordField.text()

        if len(username) == 0 or len(password) == 0:
            self.errorField.setText("Please complete all fields")

        else:
            connection = sqlite3.connect("accounts.db")
            cursor = connection.cursor()
            query = 'SELECT Password FROM People WHERE Username =\''+username+"\'"
            cursor.execute(query)
            result_pass = cursor.fetchone()
            if result_pass is not None:
                if result_pass[0] == password:
                    print("Successfully logged in")
                    self.errorField.setText("")
                    self.go_to_dashboard_window()
                    widget.setFixedSize(1280, 720)
                    widget.move(300, 160)
                else:
                    self.errorField.setText("Invalid username or password")
            else:
                self.errorField.setText("Invalid username or password")


# ------------------------------MAIN------------------------------ #


application = QApplication(sys.argv)
main = MainWindow()
widget = QStackedWidget()
widget.addWidget(main)
widget.setFixedSize(709, 599)
widget.show()
try:
    sys.exit(application.exec_())
except SystemExit:
    print("Exiting")
