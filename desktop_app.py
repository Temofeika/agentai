import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QLineEdit, QTextEdit, QPushButton, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtSvgWidgets import QSvgWidget
from agent import Agent

class AgentThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, agent, user_input):
        super().__init__()
        self.agent = agent
        self.user_input = user_input

    def run(self):
        def callback(msg):
            self.update_signal.emit(msg)
        
        response = self.agent.chat(self.user_input, output_callback=callback)
        self.finished_signal.emit(response)

class ChatDialog(QDialog):
    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.setWindowTitle("Chat with Pet")
        self.resize(400, 500)
        
        layout = QVBoxLayout()
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me something...")
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)
        self.thread = None

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.chat_history.append(f"<b>You:</b> {text}")
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        self.thread = AgentThread(self.agent, text)
        self.thread.update_signal.connect(self.on_agent_update)
        self.thread.finished_signal.connect(self.on_agent_finished)
        self.thread.start()

    def on_agent_update(self, msg):
        self.chat_history.append(f"<i>{msg}</i>")

    def on_agent_finished(self, response):
        self.chat_history.append(f"<b>Pet:</b> {response}<br>")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = Agent()
        
        # Transparent, frameless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # Load the alpaca-hat SVG
        self.svg_widget = QSvgWidget("alpaca-hat.svg")
        self.svg_widget.setFixedSize(150, 150)
        
        # Enable transparent background for SVG
        self.svg_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout.addWidget(self.svg_widget)
        
        self.old_pos = None
        self.chat_dialog = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            # Open chat on right click
            self.open_chat()

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_chat()

    def open_chat(self):
        if self.chat_dialog is None:
            self.chat_dialog = ChatDialog(self.agent, self)
        self.chat_dialog.show()
        self.chat_dialog.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
