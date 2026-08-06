import sys
import os
from dotenv import load_dotenv

def main():
    # Check if running as compiled executable
    if getattr(sys, 'frozen', False):
        env_path = os.path.join(os.path.dirname(sys.executable), '.env')
    else:
        env_path = '.env'
        
    load_dotenv(env_path)
    api_key = os.environ.get("NVIDIA_API_KEY")
    
    from PyQt6.QtWidgets import QApplication, QInputDialog, QMessageBox
    qapp = QApplication(sys.argv)
    
    # Prompt for API key if missing or default
    if not api_key or api_key == "your_nvidia_api_key_here":
        text, ok = QInputDialog.getText(None, "NVIDIA API Key Required", 
                                        "Пожалуйста, введите ваш NVIDIA NIM API Key:\n(Он сохранится в файл .env рядом с программой)")
        if ok and text.strip():
            api_key = text.strip()
            # Save it so user doesn't have to enter it again
            try:
                with open(env_path, 'w') as f:
                    f.write(f"NVIDIA_API_KEY={api_key}\n")
                os.environ["NVIDIA_API_KEY"] = api_key
            except Exception as e:
                QMessageBox.warning(None, "Warning", f"Не удалось сохранить ключ в {env_path}: {e}")
        else:
            QMessageBox.critical(None, "Ошибка", "Без API ключа агент не сможет работать. Программа будет закрыта.")
            sys.exit(1)
            
    # Key is present, launch the pet
    import desktop_app
    pet = desktop_app.DesktopPet()
    pet.show()
    sys.exit(qapp.exec())

if __name__ == "__main__":
    main()
