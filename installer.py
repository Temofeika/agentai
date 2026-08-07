import sys
import os
import shutil
import urllib.request
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal

TESSERACT_URL = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
AGENT_EXE_NAME = "AI-Agent.exe"
TARGET_DIR_NAME = "AIPet"

class InstallerThread(QThread):
    progress_update = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str)

    def run(self):
        try:
            # 1. Download Tesseract
            self.progress_update.emit(10, "Скачивание Tesseract OCR (около 40 МБ)...")
            temp_dir = Path(os.environ.get("TEMP", "."))
            tesseract_installer = temp_dir / "tesseract_setup.exe"
            
            def report_hook(count, block_size, total_size):
                if total_size > 0:
                    progress = int(count * block_size * 100 / total_size)
                    # mapping 0-100 to 10-50
                    mapped_progress = 10 + int(progress * 0.4)
                    self.progress_update.emit(mapped_progress, f"Скачивание Tesseract OCR... {progress}%")

            urllib.request.urlretrieve(TESSERACT_URL, str(tesseract_installer), reporthook=report_hook)

            # 2. Install Tesseract
            self.progress_update.emit(50, "Установка Tesseract OCR (в фоновом режиме)...")
            try:
                subprocess.run([str(tesseract_installer), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], check=True)
            except Exception as tess_e:
                print(f"Failed to install tesseract: {tess_e}")
                self.progress_update.emit(60, "Tesseract не установился, но Питомец продолжит установку...")
            
            # Clean up installer
            try:
                os.remove(tesseract_installer)
            except:
                pass

            # 3. Extract and Copy AI Agent
            self.progress_update.emit(80, "Копирование файлов питомца...")
            
            # Find the bundled exe
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(os.path.dirname(os.path.abspath(__file__)))
                
            bundled_exe = base_path / AGENT_EXE_NAME
            
            # Target path
            local_app_data = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
            target_dir = local_app_data / TARGET_DIR_NAME
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_exe = target_dir / "AI-Agent.exe"
            
            if bundled_exe.exists():
                shutil.copy2(bundled_exe, target_exe)
            else:
                self.progress_update.emit(85, "ВНИМАНИЕ: Файл питомца не найден в установщике (режим тестирования).")
                target_exe = None

            # 4. Create Desktop Shortcut
            self.progress_update.emit(90, "Создание ярлыка на рабочем столе...")
            if target_exe and target_exe.exists():
                desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
                shortcut_path = desktop / "AI Питомец.lnk"
                
                try:
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(str(shortcut_path))
                    shortcut.Targetpath = str(target_exe)
                    shortcut.WorkingDirectory = str(target_dir)
                    shortcut.IconLocation = str(target_exe)
                    shortcut.save()
                except ImportError:
                    self.progress_update.emit(95, "win32com не установлен, создание ярлыка пропущено.")

            self.progress_update.emit(100, "Установка успешно завершена!")
            self.finished_signal.emit(True, "Готово!")
            
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class InstallerWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Установка AI Питомец")
        self.resize(400, 150)
        
        layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Подготовка к установке...")
        self.status_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.thread = InstallerThread()
        self.thread.progress_update.connect(self.on_progress)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()
        
    def on_progress(self, val, text):
        self.progress_bar.setValue(val)
        self.status_label.setText(text)
        
    def on_finished(self, success, msg):
        if success:
            self.status_label.setText("Установка завершена! Можете закрыть это окно.")
            self.status_label.setStyleSheet("font-size: 13px; color: green; font-weight: bold;")
        else:
            self.status_label.setText(f"Ошибка: {msg}")
            self.status_label.setStyleSheet("font-size: 13px; color: red;")
            
        # Change progress bar to 100% anyway if error to stop animation, or keep at error point
        if success:
            self.progress_bar.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec())
