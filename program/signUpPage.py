import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

class SignUpPage(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("ui files/signUpPage.ui", self)
        self.setWindowTitle("Sign Up Page")

        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py
    
    def setController(self, controller):
        self.controller = controller

if __name__ == "__main__":
    # Temp load page to test when I run this file. main.py will be the file that runs everything else
    app = QApplication(sys.argv)
    window = SignUpPage() # Create instance of SignUpPage
    window.show()
    sys.exit(app.exec())