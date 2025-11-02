import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

class TeacherDashboard(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/teacherDashboardPage.ui", self)
        self.setWindowTitle("Your Dashboard")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.goToClassManagement.clicked.connect(lambda: self.controller.handlePageChange("manageClass"))
        self.goToHomeworkManagement.clicked.connect(lambda: self.controller.handlePageChange("manageHomework"))
        self.goToStatisticsManagement.clicked.connect(lambda: self.controller.handlePageChange("teacherStatistics"))
    
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller