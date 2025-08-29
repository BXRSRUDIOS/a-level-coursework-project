import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

class StudentDashboard(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("ui files/studentDashboardPage.ui", self)
        self.setWindowTitle("Your Dashboard")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.goToNotes.clicked.connect(lambda: self.controller.handlePageChange("chooseNotes"))
        self.goToQuestionTopics.clicked.connect(lambda: self.controller.handlePageChange("chooseQuestionTopic"))
        self.goToClass.clicked.connect(lambda: self.controller.handlePageChange("viewClassesStudent"))
        self.goToHomework.clicked.connect(lambda: self.controller.handlePageChange("viewHomeworkStudent"))
        self.goToStatistics.clicked.connect(lambda: self.controller.handlePageChange("studentStatistics"))
        self.goToStreaksGoals.clicked.connect(lambda: self.controller.handlePageChange("streakAndGoals"))

    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller