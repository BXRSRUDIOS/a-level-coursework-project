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
        self.submitButton.clicked.connect(self.submit) # Temporary, submit button will be its own function later on
    
    def setController(self, controller):
        self.controller = controller
    
    def submit(self):
        # Used for the submit button to check for validation and perform all the checks required & then store to database
        # Remember to do valid page switching afterwards

        # Take all user input from the form
        firstname = self.firstNameEnter.text()
        surname = self.surnameEnter.text()
        username = self.usernameEnter.text()
        emailAddress = self.emailEnter.text()
        password = self.passwordEnter.text()
        accountType = ""
        checked = True

        # Check to see if teacher or student has been selected or if neither have been selected
        if not(self.studentRadio.isChecked() or self.teacherRadio.isChecked()):
            checked = False
        elif self.studentRadio.isChecked():
            accountType = "Student"
        elif self.teacherRadio.isChecked():
            accountType = "Teacher"

        # Forced Presence Check regardless of whether a validation function handles it or not
        if firstname == "" or surname == "" or username == "" or emailAddress == "" or password == "" or checked == False:
            print("Some information hasn't been entered") # Replace with Popup afterwards
        else:
            self.controller.createUserReference(firstname, surname, username, emailAddress, accountType)

        