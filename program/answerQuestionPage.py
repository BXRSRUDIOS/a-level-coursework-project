import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget # type: ignore
from PyQt6 import uic # type: ignore

class AnswerQuestions(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("ui files/answerQuestionPage.ui", self)
        self.setWindowTitle("Answer Questions Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, this button will be its own function later on
        
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller