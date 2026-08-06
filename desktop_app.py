import sys
import os
import pygetwindow as gw
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QDialog, QHBoxLayout, QScrollArea, QFrame, QGraphicsDropShadowEffect, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QCursor, QFont, QColor
from PyQt6.QtSvgWidgets import QSvgWidget
from agent import Agent

class AgentThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, agent, user_input, context):
        super().__init__()
        self.agent = agent
        self.user_input = user_input
        self.context = context

    def run(self):
        def callback(msg):
            self.update_signal.emit(msg)
        
        response = self.agent.chat(self.user_input, context=self.context, output_callback=callback)
        self.finished_signal.emit(response)

class ChatDialog(QDialog):
    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.parent_pet = parent
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(350, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Main container with glassmorphism
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(240, 242, 245, 230);
                border-radius: 20px;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid rgba(0, 0, 0, 20);
                border-radius: 15px;
                background-color: rgba(255, 255, 255, 180);
                font-size: 13px;
            }
            QPushButton {
                background-color: #0084ff;
                color: white;
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0073e6;
            }
            QPushButton:disabled {
                background-color: #a0c9eb;
            }
            QComboBox {
                padding: 8px 15px;
                border: 1px solid rgba(0, 0, 0, 20);
                border-radius: 15px;
                background-color: rgba(255, 255, 255, 180);
                font-size: 12px;
                color: #333;
            }
            QComboBox::drop-down {
                border: none;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 10);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 40);
                min-height: 20px;
                border-radius: 3px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Window selector
        self.window_selector = QComboBox()
        self.window_selector.addItem("Весь экран")
        self.update_windows_list()
        layout.addWidget(self.window_selector)

        # Scroll area for chat messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet("background-color: transparent; border: none;")
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch() # Push messages up
        
        self.scroll_area.setWidget(self.chat_widget)
        layout.addWidget(self.scroll_area)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Вопрос или команда...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("➤")
        self.send_button.setFixedWidth(40)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        main_layout.addWidget(self.container)
        self.thread = None
        self.current_thinking_bubble = None
        
        # Welcome message
        self.add_message("Питомец", (
            "Привет! 🦙\n"
            "Я парю прямо тут!\n"
            "Вы можете выбрать нужное окно сверху, и я буду смотреть только на него."
        ), is_user=False)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.update_windows_list()
        self.reposition()
        
    def reposition(self):
        if self.parent_pet:
            pet_geom = self.parent_pet.geometry()
            x = pet_geom.x() - (self.width() - pet_geom.width()) // 2
            y = pet_geom.y() - self.height() + 30
            self.move(x, y)

    def update_windows_list(self):
        current_text = self.window_selector.currentText()
        self.window_selector.clear()
        self.window_selector.addItem("Весь экран")
        
        try:
            titles = [w for w in gw.getAllTitles() if w.strip()]
            # Filter out some system windows
            titles = [t for t in titles if t not in ["Program Manager", "Settings", "AI Питомец"]]
            for t in titles[:20]: # Limit to avoid huge lists
                self.window_selector.addItem(t)
        except Exception:
            pass
            
        index = self.window_selector.findText(current_text)
        if index >= 0:
            self.window_selector.setCurrentIndex(index)

    def add_message(self, sender, text, is_user=True, is_thinking=False):
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 132, 255, 230);
                    color: white;
                    border-radius: 15px;
                    padding: 10px 14px;
                    font-size: 13px;
                }
            """)
        elif is_thinking:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: rgba(0, 0, 0, 120);
                    font-size: 12px;
                    font-style: italic;
                    padding: 5px 14px;
                    border: none;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 230);
                    color: #1c1e21;
                    border-radius: 15px;
                    padding: 10px 14px;
                    font-size: 13px;
                    border: 1px solid rgba(0, 0, 0, 15);
                }
            """)
            
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        bubble.setMaximumWidth(260)
        
        if is_user:
            row_layout.addStretch()
            row_layout.addWidget(bubble)
        elif is_thinking:
            row_layout.addWidget(bubble)
            row_layout.addStretch()
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch()
            
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, row_widget)
        
        QApplication.processEvents()
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        return row_widget

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        selected_window = self.window_selector.currentText()
        context = selected_window if selected_window != "Весь экран" else None
        
        self.add_message("You", text, is_user=True)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        self.thread = AgentThread(self.agent, text, context)
        self.thread.update_signal.connect(self.on_agent_update)
        self.thread.finished_signal.connect(self.on_agent_finished)
        self.thread.start()

    def on_agent_update(self, msg):
        self.current_thinking_bubble = self.add_message("Pet", msg, is_user=False, is_thinking=True)

    def on_agent_finished(self, response):
        self.add_message("Pet", response, is_user=False)
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = Agent()
        
        # Transparent, frameless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
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
            self.open_chat()

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()
        if self.chat_dialog and self.chat_dialog.isVisible():
            self.chat_dialog.reposition()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_chat()

    def open_chat(self):
        if self.chat_dialog is None:
            self.chat_dialog = ChatDialog(self.agent, self)
        
        if self.chat_dialog.isVisible():
            self.chat_dialog.hide()
        else:
            self.chat_dialog.show()
            self.chat_dialog.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
