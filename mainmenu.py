import sqlite3
import re
import bcrypt
import resources
import dashboard
from PyQt5.QtCore import Qt, QTimer
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget
from PyQt5.QtCore import *

widget = None
is_logged_in = False


# ------------------------MAIN_WINDOW------------------------ #


class MainWindow(QDialog):
    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi("mainwindow.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.loginButton.clicked.connect(self.go_to_login)
        self.registerButton.clicked.connect(self.go_to_register)
        self.setFixedSize(800, 600)


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
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        connection = sqlite3.connect("accounts.db")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM People WHERE Username=?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            self.errorRegister.setText("Username already exists. Please choose a different username.")
            return

        if len(username) == 0 or len(password) == 0 or len(password_confirm) == 0:
            self.errorRegister.setText("Please complete all fields")

        elif password != password_confirm:
            self.errorRegister.setText("Passwords do not match.")

        elif not re.match(password_pattern, password):
            self.errorRegister.setText(
                "• Parola trebuie să conțină minim 8 caractere\n"
                "• Parola trebuie să conțină minim o majusculă\n"
                "• Parola trebuie să conțină minim o cifră \n"
                "• Parola trebuie să conțină minim un caracter special")

        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # hash la parola intr-un string hexadecimal

            user_info = [username, hashed_password]
            cursor.execute('INSERT INTO People (Username, Password) VALUES (?,?)', user_info)
            connection.commit()

            print("Successfully registered the user")
            self.go_to_main_window()

        connection.close()

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
        self.setFixedSize(800, 600)

    def go_to_main_window(self):
        backlogin_button = MainWindow()
        widget.addWidget(backlogin_button)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_dashboard_window(self):
        dashboard.widget = widget
        connection_data = self.userField.text()
        dashboard.DashboardWindow(connection_data)

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
            connection.close()
            if result_pass is not None:
                if bcrypt.checkpw(password.encode('utf-8'), result_pass[0]):  # comparare parola criptata din baza de date cu parola criptata introdusa de user
                    print("Successfully logged in")
                    self.errorField.setText("")
                    self.go_to_dashboard_window()

                else:
                    self.errorField.setText("Nume de utilizator sau parolă invalide")
            else:
                self.errorField.setText("Nume de utilizator sau parolă invalide")

