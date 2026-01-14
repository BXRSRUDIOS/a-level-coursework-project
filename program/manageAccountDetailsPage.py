import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

class ManageAccountDetails(QMainWindow):
    @handle_exceptions
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/modifyAccountPage.ui", self)
        self.setWindowTitle("Manage Account Details Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, this button will be its own function later on

        self.saveChanges.clicked.connect(lambda: self.confirmation())

    @handle_exceptions
    def confirmation(self):
        # Function to show a confirmation popup before saving changes
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("Confirm Changes")
        dialogueBox.setIcon(QMessageBox.Icon.Question)
        dialogueBox.setText("Are you sure you want to save these changes to your account?")
        dialogueBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        response = dialogueBox.exec()

        if response == QMessageBox.StandardButton.Yes:
            self.saveAccountChanges()

    @handle_exceptions
    def saveAccountChanges(self):
        # Function which will save the account changes made by the user
        # Get the data from the input fields
        newUsername = self.enterUsername.text()
        newEmail = self.enterEmail.text()
        newPassword = self.enterPassword.text()
        confirmPassword = self.confirmPassword.text()
        newFirstName = self.enterFirstName.text()
        newSurname = self.enterSurname.text()

        # Validate and update the details accordingly
        # Only update if the field is not empty
        # Allows for multiple changes at once
        # Calls relevant update functions
        if newUsername:
            self.updateUsername(newUsername) 
        if newEmail:
            self.updateEmail(newEmail)
        if newPassword and newPassword == confirmPassword:
            self.updatePassword(newPassword)
        else:
            # Show popup for password mismatch
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Input")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Please ensure you have entered and confirmed your new password correctly.")
            dialogueBox.exec()
        if newFirstName:
            self.updateFirstName(newFirstName)
        if newSurname:
            self.updateSurname(newSurname)

    @handle_exceptions
    def updateUsername(self, newUsername):
        print("Username updated to:", newUsername)
    
    @handle_exceptions
    def updateEmail(self, newEmail):
        print("Email updated to:", newEmail)
        
    @handle_exceptions
    def updatePassword(self, newPassword):
        print("Password updated to:", newPassword)

    @handle_exceptions
    def updateFirstName(self, newFirstName):
        if newFirstName == self.controller.user.firstName: # Check if the new first name is different from the current one
            # Show popup for invalid input
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Input")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Please ensure your new first name is different from the current one.")
            dialogueBox.exec()
        else: # Update the first name in the user object and database
            self.controller.user.firstName = newFirstName # Update the user object

            # Update the database
            if self.controller.user.accountType == "Student":
                query = "UPDATE student SET firstname = %s WHERE username = %s" 
            elif self.controller.user.accountType == "Teacher":
                query = "UPDATE teacher SET firstname = %s WHERE username = %s"
            values = (newFirstName, self.controller.user.username)
            self.controller.database(query, parameter=values, queryType="changeDatabase")

    @handle_exceptions
    def updateSurname(self, newSurname):
        if newSurname == self.controller.user.surname: # Check if the new surname is different from the current one
            # Show popup for invalid input
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Input")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Please ensure your new surname is different from the current one.")
            dialogueBox.exec()
        else: # Update the surname in the user object and database
            self.controller.user.surname = newSurname # Update the user object

            # Update the database
            if self.controller.user.accountType == "Student":
                query = "UPDATE student SET surname = %s WHERE username = %s" 
            elif self.controller.user.accountType == "Teacher":
                query = "UPDATE teacher SET surname = %s WHERE username = %s"
            values = (newSurname, self.controller.user.username)
            self.controller.database(query, parameter=values, queryType="changeDatabase")

    @handle_exceptions
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller