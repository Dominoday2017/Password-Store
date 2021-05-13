from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from cryptography.fernet import Fernet
import pyperclip
import os
import sys


class LoginWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('login.ui', self)
        self.registration_label.hide()
        self.show()
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)

    def login(self):
        username = self.username_lineEdit.text()
        password = self.password_lineEdit.text()
        with open("login.txt", "r") as file:
            key = file.readline()
            username_e = file.readline()
            password_e = file.readline()

            key = self.make_correct(key)
            username_e = self.make_correct(username_e)
            password_e = self.make_correct(password_e)

            username_e = self.decrypt(username_e.encode(), key).decode()
            password_e = self.decrypt(password_e.encode(), key).decode()

            if username == username_e and password == password_e:
                self.accept()
            else:
                warning = QMessageBox.warning(None, 'Login error', "Wrong username or password")

    def register(self):
        username = self.username_lineEdit.text()
        password = self.password_lineEdit.text()
        if username == "" or password == "":
            warning = QMessageBox.warning(None, 'Login error', "Username or password is empty")
        else:
            key = Fernet.generate_key()
            username = self.encrypt(username.encode(), key)
            password = self.encrypt(password.encode(), key)
            with open("login.txt", "w") as file:
                file.write(repr(key) + "\n")
                file.write(repr(username) + "\n")
                file.write(repr(password) + "\n")
                file.close()

            self.username_lineEdit.clear()
            self.password_lineEdit.clear()
            self.destroy_data()
            self.registration_label.setStyleSheet("background-color: green")
            self.registration_label.show()

    def encrypt(self, message: bytes, key: bytes) -> bytes:
        return Fernet(key).encrypt(message)

    def decrypt(self, token: bytes, key: bytes) -> bytes:
        return Fernet(key).decrypt(token)

    def make_correct(self, text):
        text = text.replace("\n", "")
        return text[2:] + text[:-1]

    def destroy_data(self):
        with open("key.txt", "w") as key:
            pass
        with open("passwords.txt", "w") as password:
            pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('gui.ui', self)
        self.setWindowTitle('Password Storager')
        self.show()
        self.gen_key()
        self.display_data()
        self.notification_label.hide()
        self.addItem_btn.clicked.connect(self.add_password)
        self.deleteItem_btn.clicked.connect(self.delete_password)
        self.resetApp_btn.clicked.connect(self.reset_app)
        self.copy_btn.clicked.connect(self.copy_password)

    def add_password(self):
        password_input = self.addItem_lineEdit.text()
        key = self.read_key()

        if password_input == "":
            warning = QMessageBox.warning(None, 'Error', "You can't add empty element")
        else:
            password_input = password_input.split("//")
            if len(password_input) >= 3:
                name, mail, password, *other = password_input
                if other:
                    encrypted_password = self.encrypt(password.encode(), key)
                    encrypted_mail = self.encrypt(mail.encode(), key)
                    encrypted_name = self.encrypt(name.encode(), key)
                    to_file = str(repr(encrypted_name)) + "//" + str(repr(encrypted_mail)) + "//" + str(repr(encrypted_password)) + "//"
                    other_string = ""
                    for x in other:
                        other_string += x
                    other_string = str(repr(self.encrypt(other_string.encode(), key)))
                    to_file = to_file + other_string
                    self.save_string_to_file(to_file)
                    self.passwordList_widget.clear()
                    self.display_data()
                else:
                    encrypted_password = self.encrypt(password.encode(), key)
                    encrypted_mail = self.encrypt(mail.encode(), key)
                    encrypted_name = self.encrypt(name.encode(), key)
                    to_file = str(repr(encrypted_name)) + "//" + str(repr(encrypted_mail)) + "//" + str(repr(encrypted_password))
                    self.save_string_to_file(to_file)
                    self.passwordList_widget.clear()
                    self.display_data()
                self.addItem_lineEdit.setText("")
            else:
                warning = QMessageBox.warning(None, 'Error', "Error input data")

    def display_data(self):
        key = self.read_key()
        with open("passwords.txt", "r") as file:
            for line in file:
                line = line.split("//")
                name, mail, password, *other = line
                password = self.make_correct(password)
                mail = self.make_correct(mail)
                name = self.make_correct(name)
                try:
                    password_decrypted = self.decrypt(password.encode(), key).decode()
                    mail_decrypted = self.decrypt(mail.encode(), key).decode()
                    name_decrypted = self.decrypt(name.encode(), key).decode()
                except:
                    warning = QMessageBox.warning(None, 'Error', "Your key is invalid \n \n Reset app.")
                    break
                if other:
                    result = name_decrypted + " mail: " + mail_decrypted + " H: " + password_decrypted + " other: "
                    other_string = ""
                    for x in other:
                        other_string += x
                    try:
                        other_string = self.make_correct(other_string)
                        other_string = self.decrypt(other_string.encode(), key).decode()
                        result = result + str(repr(other_string))
                    except:
                        warning = QMessageBox.warning(None, 'Error', "Your key is invalid \n \n Reset app.")
                    self.passwordList_widget.addItem(result)
                else:
                    result = name_decrypted + " mail: " + mail_decrypted + " H: " + password_decrypted
                    self.passwordList_widget.addItem(result)

    def save_string_to_file(self, input_string):
        with open("passwords.txt", "a+") as file:
            file.write(input_string + "\n")

    def delete_password(self):
        try:
            element_number = self.passwordList_widget.currentRow()
            data = []
            with open("passwords.txt", "r") as file:
                for line in file:
                    line.replace("\n", "")
                    data.append(line)
                data.pop(element_number)
                file.close()

            with open("passwords.txt", "w") as new_file:
                for x in data:
                    new_file.write(x)
                new_file.close()
            self.passwordList_widget.clear()
            self.display_data()
        except:
            warning = QMessageBox.warning(None, 'Error', "Delete password error")

    def copy_password(self):
        element_number = self.passwordList_widget.currentRow()
        with open("passwords.txt", "r") as file:
            for index, element in enumerate(file):
                if index == element_number:
                    element = element.split("//")
                    password = element[2]
                    password = password[2:] + password[:-1]
                    key = self.read_key()
                    password = self.decrypt(password.encode(), key).decode()
                    pyperclip.copy(password)
                    spam = pyperclip.paste()
                    self.display_notification("Password copied to clipborad", "green")

    def display_notification(self, text, color):
        self.notification_label.show()
        self.notification_label.setText(text)
        self.notification_label.setStyleSheet("background-color: " + color)

    def hide_notification(self):
        self.notification_label.hide()

    def reset_app(self):
        self.passwordList_widget.clear()
        with open("key.txt", "w") as key:
            pass
        with open("passwords.txt", "w") as password:
            pass
        self.hide()
        self.__init__()

    def encrypt(self, message: bytes, key: bytes) -> bytes:
        return Fernet(key).encrypt(message)

    def decrypt(self, token: bytes, key: bytes) -> bytes:
        return Fernet(key).decrypt(token)

    def gen_key(self):
        if os.stat("key.txt").st_size == 0:
            with open("key.txt", "wb+") as file:
                key = Fernet.generate_key()
                warning = QMessageBox.warning(None, 'Key', "New key generated. All passwords in storage are now invalid.")
                file.write(key)
                file.close()
        else:
            pass

    def read_key(self):
        with open("key.txt", "rb") as file:
            key = file.readline()
            file.close()
            return key

    def create_password_file(self):
        with open("passwords.txt", "x") as file:
            pass

    def make_correct(self, text):
        text = text.replace("\n", "")
        return text[2:] + text[:-1]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWidget()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())