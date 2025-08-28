import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

class LoginPage(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("ui files/loginPage.ui", self)
        self.setWindowTitle("Login Up Page")

        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py 

        # Connect button signals to their respective functions
        
    
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller

if __name__ == "__main__":
    # Temp load page to test when I run this file. main.py will be the file that runs everything else
    app = QApplication(sys.argv)
    window = LoginPage() # Create instance of LoginPage
    window.show()
    sys.exit(app.exec())