import sys
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    if not os.environ.get("NVIDIA_API_KEY") or os.environ.get("NVIDIA_API_KEY") == "your_nvidia_api_key_here":
        print("Please set your NVIDIA_API_KEY in the .env file.")
        sys.exit(1)
        
    # Start Desktop App
    from desktop_app import app, DesktopPet, QApplication
    import desktop_app
    
    qapp = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(qapp.exec())

if __name__ == "__main__":
    main()
