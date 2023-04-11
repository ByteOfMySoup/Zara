import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QMenu, \
    QAction, QMessageBox, QTextBrowser
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject


class Communicate(QObject):
    message_received = pyqtSignal(str, str)  # added sender argument to signal


class ChatGUI(QWidget):
    def __init__(self, communicator):
        super().__init__()
        self.communicator = communicator
        self.initUI()

    def initUI(self):
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setFont(QFont('Arial', 14))

        self.message_input = QLineEdit()
        self.message_input.setFont(QFont('Arial', 14))

        send_button = QPushButton('Send')
        send_button.setFont(QFont('Arial', 14))
        send_button.clicked.connect(self.send_message)

        self.message_input.returnPressed.connect(send_button.click)

        hbox = QHBoxLayout()
        hbox.addWidget(self.message_input)
        hbox.addWidget(send_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.chat_history)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('Chat')
        self.showMaximized()

        self.chat_history.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_history.customContextMenuRequested.connect(self.show_context_menu)

        self.communicator.message_received.connect(self.receive_message)

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.chat_history.append('You: ' + message)
            self.message_input.clear()

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
        if message.startswith('|sys|'):
            message = '<span style="background-color: yellow;">{}</span>'.format(message)
        else:
            message = '{}: {}'.format(sender, message)
        self.chat_history.append('{}: {}'.format(sender, message))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    communicator = Communicate()
    gui = ChatGUI(communicator)
    communicator.message_received.emit('Alice', 'Hello from Alice!')  # example of receiving message from Alice
    communicator.message_received.emit('Bob', 'Hi there!')  # example of receiving message from Bob
    sys.exit(app.exec_())
