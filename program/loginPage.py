from datetime import datetime, date, timedelta
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

class LoginPage(QMainWindow):
    @handle_exceptions
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/loginPage.ui", self)
        self.setWindowTitle("Login Up Page")

        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py 

        # Connect button signals to their respective functions
        self.returnHome.clicked.connect(lambda: self.controller.handlePageChange("home"))
        self.submitButton.clicked.connect(self.submit)
        self.attempts = 0 # To track the number of failed login attempts for blocking purposes
    
    @handle_exceptions
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller

    @handle_exceptions
    def loginPopups(self, type):
        # Create message box
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("Invalid Input")
        dialogueBox.setIcon(QMessageBox.Icon.Information)

        # Set message to relevant type for validation then execute the message box
        if type == "presence":
            dialogueBox.setText("Please ensure you've entered all the information & selected one of the teacher or student account options")
        elif type == "username":
            dialogueBox.setText("Please ensure your username is in a valid format and is a unique username. It may or may not exist in our system so ensure an account has also been created for this username.")
        elif type == "email":
            dialogueBox.setText("Please ensure your email is in a valid format and is a unique email address. It may or may not exist in our system so ensure an account has also been created for this email.")
        elif type == "password":
            dialogueBox.setText("Please ensure your password is correctly entered. Passwords are case sensitive.")
        elif type == "success":
            dialogueBox.setText("Success! Welcome to your new account")
        dialogueBox.exec()

    @handle_exceptions
    def checkUsernameInDatabaseForUserReference(self, username, accountType):
        # Function to check if the username exists in the database for login reference
        if accountType == "Student": # Check account type
            query = "SELECT firstname, surname, emailAddress, hashedpassword, salt FROM student WHERE username = %s" # Get the relevant user details from the database
            # This data isn't entered by the user but is needed for login verification and to load the user's dashboard
        elif accountType == "Teacher":
            query = "SELECT firstname, surname, emailAddress, hashedpassword, salt FROM teacher WHERE username = %s"
        values = (username,)
        result = self.controller.database(query, parameter=values, queryType="fetchItems")

        if result:
            return [result[0][0], result[0][1], result[0][2], result[0][3], result[0][4]] # Return firstname, surname, email, hashedpassword, salt
        else:
            return False

    @handle_exceptions
    def submit(self, _=None):

        # Take all user input from the form
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

        if username == "" or emailAddress == "" or password == "" or checked == False:
            self.loginPopups("presence")
            return None

        usernameCheck = self.checkUsernameInDatabaseForUserReference(username, accountType) # Check if username exists in database for login reference
        if usernameCheck == False:
            self.loginPopups("username") # Username does not exist in database
            return None
        else:
            # Unpack the returned user details
            firstname = usernameCheck[0]
            surname = usernameCheck[1]
            emailInDatabase = usernameCheck[2]
            hashedPasswordInDatabase = usernameCheck[3]
            salt = usernameCheck[4]
        
        self.controller.createUserReference(firstname, surname, username, emailAddress, accountType) # Create user reference in controller for session management
        # Forced Presence Check regardless of whether a validation function handles it or not
        
        # Main Validation Checks with Popups for invalid input
        if emailAddress != emailInDatabase:
            self.loginPopups("email") # Email does not match the one in the database
            return None
        
        hashCheck = self.controller.user.generateHashedPassword(password, salt)[0] # Generate hashed password from user input for comparison
        if hashCheck != hashedPasswordInDatabase:
            if accountType == "Student":
                self.blockUser(username) # Check if user needs to be blocked after failed login attempts, only students can be blocked
            self.loginPopups("password") # Password does not match the one in the database
            return None
        
        self.loginPopups("success") # Successful login
        if accountType == "Student":
            self.controller.handlePageChange("studentDashboard") # Change to student dashboard page upon successful login
        elif accountType == "Teacher":
            self.controller.handlePageChange("teacherDashboard") # Change to teacher dashboard page upon successful login
        
        self.controller.user.hashedPassword = hashedPasswordInDatabase
        self.controller.user.salt = salt

        # Check if they have logged in on consecutive days for streaks purposes
        status = self.checkConsecutiveDaysLoginStatus()
        self.controller.streak_and_goals.updateStreak(status)

        # Check if goals need to be reset
        if accountType == "Student":
            if self.checkGoalsReset():
                self.controller.streak_and_goals.updateGoals()
            else:
                self.controller.streak_and_goals.updateNumberOfLoginsGoal()

        self.attempts = 0 # Reset attempts after successful login
        return True
    
    @handle_exceptions
    def checkConsecutiveDaysLoginStatus(self):
        if self.controller.user.accountType == "Student":
            # Get last day logged in from database
            result = self.controller.database("SELECT lastDayLoggedIn FROM login_statuses WHERE student_id = %s;", 
                                              parameter=(self.controller.user.user_id,), 
                                              queryType="fetchItems")
            # Get yesterday's date for comparison - it is stored as a date object only so no time
            yesterday = date.today() - timedelta(days=1)
            # If yesterday's date == the current date stored in database, then they have logged in consecutive days so return true
            if result and len(result) > 0:
                lastDayLoggedIn = result[0][0]
                if lastDayLoggedIn == yesterday:
                    return True
                else:
                    return False
    @handle_exceptions
    def alreadyLoggedInToday(self):
        if self.controller.user.accountType == "Student":
            # Get alreadyLoggedInToday status from database
            result = self.controller.database("SELECT lastDayLoggedIn FROM login_statuses WHERE student_id = %s;", 
                                              parameter=(self.controller.user.user_id,), 
                                              queryType="fetchItems")
            if result and len(result) > 0:
                lastLoggedInToday = result[0][0]
                return lastLoggedInToday == date.today()
            else:
                return False
    
    @handle_exceptions
    def checkGoalsReset(self):
        if self.controller.user.accountType == "Student":
            # Get goal reset date from database
            result = self.controller.database("SELECT resetDate FROM goals WHERE student_id = %s;", 
                                              parameter=(self.controller.user.user_id,), 
                                              queryType="fetchItems")
            if result and len(result) > 0:
                goalResetDate = result[0][0]
                return goalResetDate <= date.today()
            else:
                return False
    
    @handle_exceptions
    def blockUser(self, name):
        # Get user ID
        userID = self.controller.database("SELECT id FROM student WHERE username = %s", parameter=(name,), queryType="fetchItems")[0][0]
        if userID: # Only block if userID is found
            if self.attempts == 3: # Block after 3 failed login attempts
                self.attempts = 0
                # Set to True in database
                self.controller.database("UPDATE login_statuses SET isBlocked = TRUE WHERE student_id = %s", parameter=(userID,), queryType="changeDatabase")
                # Popup Message To Say Account Blocked
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Account Blocked")
                dialogueBox.setText("Due to multiple failed login attempts, your account has been blocked. Your app use will be unblocked in around 15 minutes time.")
                dialogueBox.setIcon(QMessageBox.Icon.Critical)
                dialogueBox.exec()

                # Unblock after 15 minutes
                self.controller.database("SELECT unblockUser(%s);", parameter=(userID,), queryType="fetchItems")
            else:
                self.attempts += 1    