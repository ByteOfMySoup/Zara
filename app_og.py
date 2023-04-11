import sys
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QMenu, \
    QAction, QMessageBox, QToolBar, QToolButton
from chat import *
import pyttsx3


def text_to_speech(message):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(message)
    engine.runAndWait()


class Communicate(QObject):
    message_received = pyqtSignal(str, str)  # added sender argument to signal


class ResponseThread(QThread):
    update_chat = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super(ResponseThread, self).__init__(parent)
        self.messages = None
        self.chat_history = None

    def set_parameters(self, messages, chat_history):
        self.messages = messages
        self.chat_history = chat_history

    def run(self):
        response = get_response(self.messages, "gpt-4")
        role = response["choices"][0]["message"]["role"]
        content = response["choices"][0]["message"]["content"]
        self.update_chat.emit(role, content)
        # text_to_speech(content)
        if is_command(content):
            stdout = run(content, self.messages)
            if stdout:
                self.update_chat.emit("system", stdout)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.communicator = Communicate()
        self.initUI()

    def initUI(self):
        openai.api_key = retrieve_key()
        self.messages = Messages()
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setFont(QFont('Arial', 14))

        self.message_input = QLineEdit()
        self.message_input.setFont(QFont('Arial', 14))

        self.send_button = QPushButton('Send')
        self.send_button.setFont(QFont('Arial', 14))
        self.send_button.clicked.connect(self.send_message)

        self.message_input.returnPressed.connect(self.send_button.click)

        hbox = QHBoxLayout()
        hbox.addWidget(self.message_input)
        hbox.addWidget(self.send_button)

        vbox = QVBoxLayout()

        toolbar = QToolBar("Save Load Clear")
        save_action = QAction("Save Chat", self)
        save_action.triggered.connect(self.save_chat)
        load_action = QAction("Load Chat", self)
        load_action.triggered.connect(self.load_chat)
        clear_action = QAction("Clear Chat", self)
        clear_action.triggered.connect(self.clear_chat)
        toolbar.addAction(save_action)
        toolbar.addAction(load_action)
        toolbar.addAction(clear_action)

        vbox.addWidget(toolbar)

        vbox.addWidget(self.chat_history)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('Zara GPT-4')
        self.showMaximized()

        self.chat_history.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_history.customContextMenuRequested.connect(self.show_context_menu)

        self.communicator.message_received.connect(self.receive_message)

        self.response_thread = ResponseThread()
        self.response_thread.update_chat.connect(self.receive_message)

        self.initMessages()

    def initMessages(self):
        for message in self.messages.all():
            tar = self.messages.all().index(message)
            if tar == 0:
                continue
            role, content = decompile_message(message)
            self.chat_history.append(f"{role}: {content}")
            self.message_input.clear()

    def load_response(self):
        self.response_thread.set_parameters(self.messages, self.chat_history)
        self.response_thread.start()

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.send_button.setEnabled(False)
            self.messages.insert("user", message)
            self.chat_history.append('user: ' + message)
            self.message_input.clear()
            self.load_response()

    def show_context_menu(self, pos):
        cursor = self.chat_history.cursorForPosition(pos)
        cursor.select(QTextCursor.LineUnderCursor)
        menu = QMenu(self.chat_history)
        delete_action = QAction('Delete', self.chat_history)
        delete_action.triggered.connect(lambda: self.delete_message(cursor))
        menu.addAction(delete_action)
        menu.exec_(self.chat_history.mapToGlobal(pos))

    def delete_message(self, cursor):
        cursor.select(QTextCursor.LineUnderCursor)
        selected_text = cursor.selectedText()
        reply = QMessageBox.question(self, 'Delete Message', 'Are you sure you want to delete this message?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor.removeSelectedText()

    def receive_message(self, sender, message):  # added sender argument
        self.messages.insert(sender, message)
        self.chat_history.append(f"{sender}: {message}")
        if sender == "system":
            self.send_button.setEnabled(False)
            print("system message detected")
            print(self.messages.latest())
            self.load_response()
        else:
            self.send_button.setEnabled(True)  # Re-enable the send button

    def save_chat(self):
        self.messages.save()
        self.chat_history.append('system: Messages successfully saved.')

    def load_chat(self):
        self.messages.load()
        self.chat_history.clear()
        self.initMessages()
        self.chat_history.append('system: Messages successfully loaded.')

    def clear_chat(self):
        self.messages.clear()
        self.chat_history.clear()
        self.chat_history.append('system: Messages successfully cleared.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = App()
    sys.exit(app.exec_())
