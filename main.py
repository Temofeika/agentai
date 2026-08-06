import sys
import os
from PyQt6.QtWidgets import QApplication
import desktop_app

def main():
    qapp = QApplication(sys.argv)
            
    # Launch the pet
    pet = desktop_app.DesktopPet()
    pet.show()
    sys.exit(qapp.exec())

if __name__ == "__main__":
    main()
