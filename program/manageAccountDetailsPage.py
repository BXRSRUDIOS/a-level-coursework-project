import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions
from PyQt6.QtCore import pyqtSignal

class ManageAccountDetails(QMainWindow):
    #sendToControllerSignal = pyqtSignal(str)

    @handle_exceptions
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/modifyAccountPage.ui", self)
        self.setWindowTitle("Manage Account Details Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.returnToDashboard.clicked.connect(lambda: self.changePage())
    
        self.saveChanges.clicked.connect(lambda: self.confirmation())
    @handle_exceptions
    def checkUsernameUnique(self, username):
        # Function to check if the username is unique in the database
        if self.controller.user.accountType == "student": # Create the right query for correct account type
            query = "SELECT username FROM student WHERE username = %s"
        else:
            query = "SELECT username FROM teacher WHERE username = %s"
        parameter = (username,)
        result = self.controller.database(query, parameter, "fetchItems") # Get items

        if result: # Check if a result was returned
            return False
        else:
            return True
    @handle_exceptions
    def checkEmailUnique(self, email):
        # Function to check if the email is unique in the database
        if self.controller.user.accountType == "student":
            query = "SELECT emailaddress FROM student WHERE emailaddress = %s"
        else:
            query = "SELECT emailaddress FROM teacher WHERE emailaddress = %s"
        parameter = (email,)
        result = self.controller.database(query, parameter, "fetchItems") # Get items
        
        if result: # Check if a result was returned
            return False
        else:
            return True
        
    @handle_exceptions
    def checkUsernameIsValid(self, username, type="change"):
        # Function to check if the username is valid based on certain criteria
        # SQL Injection Prevention not needed as PostgreSQL  will handle it
        # You learn something new everyday

        # Load harmful words from the badwords.txt file
        harmfulWordsList = []
        with open("the project/program/badwords.txt", "r") as file:
            harmfulWordsList = [line.strip() for line in file.readlines()]

        # Presence Check for Username - Does it exist?
        if username is not None and username != "":

            # Length Check for Username
            if len(username) >= 8 and len(username) <= 32:
                
                # Security Check for certain terms (consists of phrases found in a file of inappropriate content)
                if username.lower() not in harmfulWordsList:

                    # Format Check For Special Characters
                    specialChars = '''!"#$%&'()*+,-./:;<=>?@[]^_`{|}~ '''
                    if not(any(char in specialChars for char in username)):

                        # Uniqueness Test using username uniqueness function
                        if type == "signup" or type == "change":
                            if self.checkUsernameUnique(username) == True:
                                # If all conditions met, return True
                                return True
                        
                            else:
                                return False
                        else:
                            return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    
    @handle_exceptions
    def checkEmailIsValid(self, email):
        # Load harmful words from the badwords.txt file
        harmfulWordsList = []
        with open("the project/program/badwords.txt", "r") as file:
            harmfulWordsList = [line.strip() for line in file.readlines()]
        
        
        # Presence Check for Email - Does it exist?
        if email is not None and email != "":
            # Length Check for email
            if len(email) >= 10 and "@" in email and (".com" in email or ".co.uk" in email or ".org" in email or ".net" in email):
                
                # Security Check for certain terms (consists of phrases found in a file of inappropriate content)
                if not any(badword in email.lower() for badword in harmfulWordsList):

                    # Format Check For Special Characters
                    specialChars = '''!"#$%&'()*+,-/:;<=>?[]^_`{|}~ '''
                    requiredChars = "@."
                    if any(char in requiredChars for char in email) and not(any(char in specialChars for char in email)):

                        # Uniqueness Test using username uniqueness function
                        if type == "signup":
                            if self.checkEmailUnique(email) == True:
                                # If all conditions met, return True
                                return True
                        
                            else:
                                return False
                        else:
                            return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    
    @handle_exceptions
    def checkPasswordStrength(self, password):
        # Function to check if the password is of valid length
        
        # Take password as a parameter so that the password isn't stored in the class

        # Get the sets of characters to find
        uppers = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "0123456789"
        specials = '''!"#$%&'()*+,-./:;<=>?@[]^_`{|}~ '''

        # Count Characters Variables
        upperCount = 0
        numberCount = 0
        specialCount = 0
        
        # Length Check for Password
        if len(password) >= 12:
            # Check for at least 2 uppercase, 2 numbers and 2 special characters
            # Increment relevant counters when found
            for char in password:
                if char in uppers:
                    upperCount += 1
                if char in numbers:
                    numberCount += 1
                if char in specials:
                    specialCount += 1
            # Check values of counters and see if they meet the criteria
            if upperCount >= 2 and numberCount >= 2 and specialCount >= 2:
                return True
            else:
                return False
        else:
            return False

    @handle_exceptions
    def changePage(self):
        # Function to change page back to the relevant dashboard
        if self.controller.user.accountType == "Student":
            self.controller.handlePageChange("studentDashboard")
        elif self.controller.user.accountType == "Teacher":
            self.controller.handlePageChange("teacherDashboard")

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
        if newUsername == self.controller.user.username: # Check if the new username is different from the current one
            # Show popup for invalid input
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Input")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Please ensure your new username is different from the current one.")
            dialogueBox.exec()
        else: # Update the username in the user object and database
            if self.checkUsernameIsValid(newUsername) == False:
                # Show popup for invalid username
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Invalid Input")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.setText("Please ensure your new username is valid.")
                dialogueBox.exec()
                return None

            # Update the database
            if self.controller.user.accountType == "Student":
                query = "UPDATE student SET username = %s WHERE username = %s" 
            elif self.controller.user.accountType == "Teacher":
                query = "UPDATE teacher SET username = %s WHERE username = %s"
            values = (newUsername, self.controller.user.username)
            self.controller.database(query, parameter=values, queryType="changeDatabase")

            self.controller.user.username = newUsername # Update the user object

            self.currentUName.setText(self.controller.user.username) # Update the displayed current username
            # Show success message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Success")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Your username has been successfully updated.")
            dialogueBox.exec()

            

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
            if self.checkEmailIsValid(newEmail) == False:
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

            self.controller.user.email = newEmail # Update the user object

            self.currentEmail.setText(self.controller.user.email) # Update the displayed current email
            # Show success message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Success")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Your email address has been successfully updated.")
            dialogueBox.exec()
        
    @handle_exceptions
    def updatePassword(self, newPassword):
        # Validate the password strength
        if not self.checkPasswordStrength(newPassword):
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
            # Update the database
            if self.controller.user.accountType == "Student":
                query = "UPDATE student SET firstname = %s WHERE username = %s" 
            elif self.controller.user.accountType == "Teacher":
                query = "UPDATE teacher SET firstname = %s WHERE username = %s"
            values = (newFirstName, self.controller.user.username)
            self.controller.database(query, parameter=values, queryType="changeDatabase")

            self.controller.user.firstName = newFirstName # Update the user object

            self.currentFName.setText(self.controller.user.firstName) # Update the displayed current first name
            # Show success message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Success")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Your first name has been successfully updated.")
            dialogueBox.exec()

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
            # Update the database
            if self.controller.user.accountType == "Student":
                query = "UPDATE student SET surname = %s WHERE username = %s" 
            elif self.controller.user.accountType == "Teacher":
                query = "UPDATE teacher SET surname = %s WHERE username = %s"
            values = (newSurname, self.controller.user.username)
            self.controller.database(query, parameter=values, queryType="changeDatabase")

            self.controller.user.surname = newSurname # Update the user object

            self.currentSName.setText(self.controller.user.surname) # Update the displayed current surname
            # Show success message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Success")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.setText("Your surname has been successfully updated.")
            dialogueBox.exec()

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