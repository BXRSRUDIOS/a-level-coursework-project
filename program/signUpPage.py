import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions
import random
import datetime

class SignUpPage(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/signUpPage.ui", self)
        self.setWindowTitle("Sign Up Page")

        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.returnHome.clicked.connect(lambda: self.controller.handlePageChange("home"))
        self.submitButton.clicked.connect(self.submit)
    
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
            dialogueBox.setWindowTitle("Success")
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
        
        # Store user account details in params for database processing because then I don't have ugly looking long code lines
        params = (self.controller.user.firstName, self.controller.user.surname, self.controller.user.username, 
                  self.controller.user.email, self.controller.user.hashedPassword, self.controller.user.salt)
        
        if self.controller.user.accountType == "Teacher": # Check account type
            # Store the teacher account & complete
            self.controller.database("""INSERT INTO teacher (firstname, surname, username, emailaddress, hashedpassword, salt)
                                     VALUES (%s, %s, %s, %s, %s, %s);
                                     """, parameter=params, 
                                     queryType="changeDatabase")
            self.controller.user.user_id = self.controller.database("SELECT id FROM teacher WHERE username = %s;", 
                                                                    parameter=(self.controller.user.username,), 
                                                                    queryType="fetchItems")[0][0]
        elif self.controller.user.accountType == "Student":
            # Store the student account
            self.controller.database("""INSERT INTO student (firstname, surname, username, emailaddress, hashedpassword, salt)
                                     VALUES (%s, %s, %s, %s, %s, %s);
                                     """, parameter=params, 
                                     queryType="changeDatabase")
            
            # Fetch student user ID with validation and logging
            result = self.controller.database("SELECT id FROM student WHERE username = %s;", 
                                              parameter=(self.controller.user.username,), 
                                              queryType="fetchItems")
            if result and len(result) > 0:
                self.controller.user.user_id = result[0][0]
            else:
                print("DEBUG: No student ID found for username:", self.controller.user.username)
                raise ValueError("No student ID found for the given username.")

            self.generateEmptyStatistics(self.controller.user.user_id)

        # Correct page switching
        if self.controller.user.accountType == "Student":
            self.controller.handlePageChange("studentDashboard")
        elif self.controller.user.accountType == "Teacher":
            self.controller.handlePageChange("teacherDashboard")
    
    @handle_exceptions
    def generateEmptyStatistics(self, user_id):
        # Start by handling the login statuses
        # Store params early to not deal with ugly code
        today = datetime.date.today() # Today's date for "lastDayLoggedIn"
        params = (user_id, True, today, False)
        self.controller.database("""INSERT INTO login_statuses (student_id, alreadyLoggedInToday, lastDayLoggedIn, isBlocked)
                                     VALUES (%s, %s, %s, %s);
                                     """, parameter=params, 
                                     queryType="changeDatabase")
        
        # Handle streaks
        self.controller.database("""INSERT INTO streaks (student_id, numberDaysStreak, longestDaysStreak)
                                     VALUES (%s, %s, %s);
                                     """, parameter=(user_id, 1, 1), 
                                     queryType="changeDatabase")
        
        # Handle Goals
        # Generate Targets
        numberLoginsNeededThisWeek = random.randint(2,5),
        numberQuestionsToAnswerThisWeek = random.randint(25,50),

        # Create a params tuple
        params = (user_id, numberLoginsNeededThisWeek, numberQuestionsToAnswerThisWeek, 1, 0, 0, 0)
        self.controller.database("""INSERT INTO goals (student_id, timesLoggedInTarget, questionsAnsweredTarget, homeworksCompletedTarget, timesLoggedIn, questionsAnswered, homeworksCompleted)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s);
                                     """, parameter=params, 
                                     queryType="changeDatabase")
        
        # Handle Overall Statistics
        params = (user_id, 0, 0, 0, 0)
        self.controller.database("""INSERT INTO statistic (student_id, noQuestionsAnswered, noCorrectQuestions, noHomeworksCompleted, noHomeworkCorrectQuestions)
                                     VALUES (%s, %s, %s, %s, %s);
                                     """, parameter=params, 
                                     queryType="changeDatabase")

        # Homework accuracy will be handled when it comes to actually completing a homework section        
        # Find the correct statistic id based on the student id so that we can deal with the topic_accuracy handles which has statistic id as a foreign key instead
        result = self.controller.database("SELECT id FROM statistic ORDER BY id DESC LIMIT 1", 
                                                                    queryType="fetchItems")
        if result and len(result) > 0:
            statistic_id = result[0][0]
        else:
            print("DEBUG: No statistic found for the given student_id.")
            raise ValueError("No statistic found for the given student_id.")
        self.controller.user.statistic_id = statistic_id # For use later on in the program for other menus

        # Finally handle topic accuracy
        # Do this using a loop to generate each one and relate to statistic id
        topics = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "2.1", "2.2", "2.3", "2.4", "2.5"]
        for i in topics:
            params = (i, 0, 0) # Set params then SQL query to store in database
            self.controller.database("""INSERT INTO topic_accuracy (topiccode, noQuestionsTopicAnswered, noCorrectTopicQuestions)
                                         VALUES (%s, %s, %s);""", 
                                     parameter=params, 
                                     queryType="changeDatabase")

            result = self.controller.database("SELECT id FROM topic_accuracy ORDER BY id DESC LIMIT 1", 
                                              queryType="fetchItems")
            if result and len(result) > 0:
                topic_id = result[0][0]
            else:
                print("DEBUG: No topic ID found for topic code:", i)
                raise ValueError("No topic id found for the given statistic id.")

            # Add topic_id & statistic_id to link table
            params = (statistic_id, topic_id)
            self.controller.database("""INSERT INTO statistic_topic_accuracy (statistic_id, topic_accuracy_id)
                                         VALUES (%s, %s);""", 
                                     parameter=params, 
                                     queryType="changeDatabase")
            
        # All relevant statistical data should now be added to database where needed for the sign up page

