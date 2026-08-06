import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QDialog, QHBoxLayout, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QCursor, QFont
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
        self.setWindowTitle("AI Питомец")
        self.resize(450, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #ccd0d5;
                border-radius: 20px;
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0084ff;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0073e6;
            }
            QPushButton:disabled {
                background-color: #a0c9eb;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f2f5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #bcc0c4;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Scroll area for chat messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch() # Push messages up
        
        self.scroll_area.setWidget(self.chat_widget)
        layout.addWidget(self.scroll_area)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Напишите сообщение...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        self.thread = None
        self.current_thinking_bubble = None
        
        # Welcome message
        self.add_message("Питомец", (
            "Привет! Я ваш умный помощник! 🦙\n\n"
            "Я умею:\n"
            "• Отвечать на любые вопросы\n"
            "• Видеть ваш экран (просто спросите: 'что на экране?')\n"
            "• Читать текст с картинок и окон\n"
            "• Конвертировать файлы"
        ), is_user=False)

    def add_message(self, sender, text, is_user=True, is_thinking=False):
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #0084ff;
                    color: white;
                    border-radius: 18px;
                    padding: 12px 16px;
                    font-size: 14px;
                }
            """)
        elif is_thinking:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: #8a8d91;
                    font-size: 13px;
                    font-style: italic;
                    padding: 5px 16px;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: white;
                    color: #1c1e21;
                    border-radius: 18px;
                    padding: 12px 16px;
                    font-size: 14px;
                    border: 1px solid #e4e6eb;
                }
            """)
            
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Max width for bubbles so they don't stretch fully
        bubble.setMaximumWidth(320)
        
        if is_user:
            row_layout.addStretch()
            row_layout.addWidget(bubble)
        elif is_thinking:
            row_layout.addWidget(bubble)
            row_layout.addStretch()
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch()
            
        # Insert before the stretch element at the end
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, row_widget)
        
        QApplication.processEvents()
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        return row_widget

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.add_message("You", text, is_user=True)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        self.thread = AgentThread(self.agent, text)
        self.thread.update_signal.connect(self.on_agent_update)
        self.thread.finished_signal.connect(self.on_agent_finished)
        self.thread.start()

    def on_agent_update(self, msg):
        if self.current_thinking_bubble:
            # Update existing thinking bubble or add to it
            pass # Keep it simple, just add new thinking messages
        self.current_thinking_bubble = self.add_message("Pet", msg, is_user=False, is_thinking=True)

    def on_agent_finished(self, response):
        if self.current_thinking_bubble:
            # We could remove thinking bubbles, but let's just leave them as history
            pass
            
        self.add_message("Pet", response, is_user=False)
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
