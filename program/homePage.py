import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

class HomePage(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/homePage.ui", self)
        self.setWindowTitle("Home Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.signUpButton.clicked.connect(self.goToSignUp)
        self.loginButton.clicked.connect(self.goToLogin)
    
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller

    def goToSignUp(self):
        # The signal from button press calls the function which calls the controller to change page
        if self.controller:
            self.controller.handlePageChange("signup")
    
    def goToLogin(self):
        # The signal from button press calls the function which calls the controller to change page
        if self.controller:
            self.controller.handlePageChange("login")