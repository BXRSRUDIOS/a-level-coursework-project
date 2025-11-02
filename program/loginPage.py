import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

class LoginPage(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/loginPage.ui", self)
        self.setWindowTitle("Login Up Page")

        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py 

        # Connect button signals to their respective functions
        self.returnHome.clicked.connect(lambda: self.controller.handlePageChange("home"))
        self.submitButton.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, submit button will be its own function later on
    
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller