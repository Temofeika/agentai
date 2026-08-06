import sys
import os

def main():
    from PyQt6.QtWidgets import QApplication
    qapp = QApplication(sys.argv)
            
    # Launch the pet
    import desktop_app
    pet = desktop_app.DesktopPet()
    pet.show()
    sys.exit(qapp.exec())

if __name__ == "__main__":
    main()
