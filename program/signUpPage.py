import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

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
    
    @handle_exceptions
    def setController(self, controller):
        self.controller = controller
    
    @handle_exceptions
    def signUpPopups(self, type):
        # Create message box
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("Invalid Input")
        dialogueBox.setIcon(QMessageBox.Icon.Information)

        # Set message to relevant type for validation then execute the message box
        if type == "presence":
            dialogueBox.setText("Please ensure you've entered all the information & selected one of the teacher or student account options")
        elif type == "username":
            dialogueBox.setText("Please ensure your username meets the following criteria:\n1. Longer than 8 characters\n2. Shorter than 32 characters\n3. Contains no special characters and bad words\n4. Is a unique username")
        elif type == "email":
            dialogueBox.setText("Please ensure your email is in a valid format of:\n1. Longer than 10 characters\n2. Contains @ Symbol\n3. Contains something equivalent to .com or .co.uk etc\n4. Is a unique email address")
        elif type == "password":
            dialogueBox.setText("Please ensure your password meets the following strength criteria:\n1. Longer than 12 characters\n2. Contains 2+ Upper Case Characters\n3. Contains 2+ Numbers\n4. Contains 2+ Special Characters")
        elif type == "success":
            dialogueBox.setText("Success! Welcome to your new account")
        dialogueBox.exec()

    @handle_exceptions
    def submit(self, _=None):
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
            self.signUpPopups("presence")
            return None
        else:
            self.controller.createUserReference(firstname, surname, username, emailAddress, accountType)

        # Perform User Class Validation Checks
        usernameValidationCheck = self.controller.user.checkUsernameIsValid()
        emailValidationCheck = self.controller.user.checkEmailIsValid()
        passwordStrengthCheck = self.controller.user.checkPasswordStrength(password)
        
        # Perform Truth Value Comparisons To See if Any Checks Return False & Take Action For This
        # Separate checks to ensure that all relevant error messages show up + return none afterwards
        if usernameValidationCheck == False:
            self.signUpPopups("username")
        if emailValidationCheck == False:
            self.signUpPopups("email")
        if passwordStrengthCheck == False:
            self.signUpPopups("password")
        if usernameValidationCheck == False or emailValidationCheck == False or passwordStrengthCheck == False:
            return None
        else:
            self.signUpPopups("success")
        
        # Create a hash (with salt) & store in user object reference
        hashedPassword, salt = self.controller.user.generateHashedPassword(password)
        self.controller.user.hashedPassword = hashedPassword
        self.controller.user.salt = salt
        
        # Add database work here


        # Correct page switching
        if self.controller.user.accountType == "Student":
            self.controller.handlePageChange("studentDashboard")
        elif self.controller.user.accountType == "Teacher":
            self.controller.handlePageChange("teacherDashboard")