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
        if newPassword:
            if newPassword == confirmPassword:
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
        if newEmail == self.controller.user.email: # Check if the new email is different from the current one
            # Show popup for invalid input
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Input")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Please ensure your new email address is different from the current one.")
            dialogueBox.exec()
        else: # Update the email in the user object and database
            self.controller.user.email = newEmail # Update the user object
            if self.controller.user.checkEmailIsValid() == False:
                # Show popup for invalid email format
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Invalid Input")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.setText("Please ensure your new email address is in a valid format.")
                dialogueBox.exec()
                return None
            # Update the database
            if self.controller.user.accountType == "Student":
                query = "UPDATE student SET emailAddress = %s WHERE username = %s" 
            elif self.controller.user.accountType == "Teacher":
                query = "UPDATE teacher SET emailAddress = %s WHERE username = %s"
            values = (newEmail, self.controller.user.username)
            self.controller.database(query, parameter=values, queryType="changeDatabase")
            
            self.currentEmail.setText(self.controller.user.email) # Update the displayed current email
        
    @handle_exceptions
    def updatePassword(self, newPassword):
        # Validate the password strength
        if not self.controller.user.checkPasswordStrength(newPassword):
            # Show popup for weak password
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Weak Password")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.setText("Your password must be at least 12 characters long and include at least 2 uppercase letters, 2 numbers, and 2 special characters.")
            dialogueBox.exec()
            return None

        # Generate hashed password and salt
        hashedPassword, salt = self.controller.user.generateHashedPassword(newPassword)

        # Update the password in the database
        if self.controller.user.accountType == "Student":
            query = "UPDATE student SET hashedPassword = %s, salt = %s WHERE username = %s"
        elif self.controller.user.accountType == "Teacher":
            query = "UPDATE teacher SET hashedPassword = %s, salt = %s WHERE username = %s"
        values = (hashedPassword, salt, self.controller.user.username)
        self.controller.database(query, parameter=values, queryType="changeDatabase")

        # Show success message
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("Success")
        dialogueBox.setIcon(QMessageBox.Icon.Information)
        dialogueBox.setText("Your password has been successfully updated.")
        dialogueBox.exec()

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
            
            self.currentFName.setText(self.controller.user.firstName) # Update the displayed current first name

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

            self.currentSName.setText(self.controller.user.surname) # Update the displayed current surname

    @handle_exceptions
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller
        self.controller.userReferenceCreated.connect(self.updateOriginalInformation)
    
    @handle_exceptions
    def updateOriginalInformation(self, username):
        # Update all user information and show on fiellds
        self.currentFName.setText(self.controller.user.firstName)
        self.currentSName.setText(self.controller.user.surname)
        self.currentUName.setText(self.controller.user.username)
        self.currentEmail.setText(self.controller.user.email)
        # Password is not shown for security reasons