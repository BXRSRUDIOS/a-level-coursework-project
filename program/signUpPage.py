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

        # Connect button signals to their respective functions
        self.returnHome.clicked.connect(lambda: self.controller.handlePageChange("home"))
        self.submitButton.clicked.connect(lambda: self.controller.handlePageChange("teacherDashboard")) # Temporary, submit button will be its own function later on
    
    def setController(self, controller):
        self.controller = controller