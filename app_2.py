import sys
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QMenu, \
    QAction, QMessageBox, QToolBar, QToolButton
from chat import *
import pyttsx3


class Communicate(QObject):
    message_received = pyqtSignal(str, str)  # added sender argument to signal


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.communicator = Communicate()
        self.initUI()

    def load_response(self):
        response = get_response(self.messages)
        self.messages.insert(response["choices"][0]["message"]["role"], response["choices"][0]["message"]["content"])
        content = self.messages.latest()["content"]
        if is_command(content):
            stdout = run(content, self.messages)
            if stdout:
                self.messages.insert("system", stdout)
                self.chat_history.append(f"system: {stdout}")
        role, content = decompile_message(self.messages.latest())
        if role == "assistant":
            self.text_to_speech(content)
        self.receive_message(role, content)
        self.send_button.setEnabled(True)

    def text_to_speech(self, message):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech
        engine.say(message)
        engine.runAndWait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = App()
    sys.exit(app.exec_())
