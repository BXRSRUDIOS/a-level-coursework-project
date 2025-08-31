# Import relevant modules
import sys
import psycopg2
import os
import io
import hashlib
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import QSize

# Import Classes for all the different pages
from homePage import HomePage
from signUpPage import SignUpPage
from loginPage import LoginPage
from studentDashboard import StudentDashboard
from teacherDashboard import TeacherDashboard
from chooseNotesPage import ChooseNotes
from chooseQuestionTopicPage import ChooseQuestionTopic
from answerQuestionPage import AnswerQuestions
from manageAccountDetailsPage import ManageAccountDetails
from viewClassesStudentPage import ViewClassesStudent
from viewHomeworkStudentPage import ViewHomeworkStudent
from streakAndGoalsPage import StreakAndGoals
from manageClassPage import ManageClass
from manageHomeworkPage import ManageHomework
from studentStatisticsPage import StudentStatistics
from teacherStatisticsPage import TeacherStatistics

# Environment variables from the .env file need loading
load_dotenv()

# Enforce UTF-8 encoding for the database connection
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Controller(QMainWindow):
    def __init__(self):
        super().__init__()
        # Setup the actual stacked widget, this will hold the different pages to select and change to when relevant
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)
        self.setFixedSize(QSize(800, 800)) # Sets fixed size for the windows

        # This should create object instances for all of the different pages
        self.home_page = HomePage()
        self.signup_page = SignUpPage()
        self.login_page = LoginPage()
        self.student_dashboard = StudentDashboard()
        self.teacher_dashboard = TeacherDashboard()
        self.choose_notes = ChooseNotes()
        self.choose_question_topic = ChooseQuestionTopic()
        self.answer_questions = AnswerQuestions()
        self.manage_account_details = ManageAccountDetails()
        self.view_classes_student = ViewClassesStudent()
        self.view_homework_student = ViewHomeworkStudent()
        self.streak_and_goals = StreakAndGoals()
        self.manage_class = ManageClass()
        self.manage_homework = ManageHomework()
        self.student_statistics = StudentStatistics()
        self.teacher_statistics = TeacherStatistics()

        # Add pages to the stack
        self.stackedWidget.addWidget(self.home_page) # Index 0 of the stacked widget
        self.stackedWidget.addWidget(self.signup_page)
        self.stackedWidget.addWidget(self.login_page)
        self.stackedWidget.addWidget(self.student_dashboard)
        self.stackedWidget.addWidget(self.teacher_dashboard)
        self.stackedWidget.addWidget(self.choose_notes)
        self.stackedWidget.addWidget(self.choose_question_topic)
        self.stackedWidget.addWidget(self.answer_questions)
        self.stackedWidget.addWidget(self.manage_account_details)
        self.stackedWidget.addWidget(self.view_classes_student)
        self.stackedWidget.addWidget(self.view_homework_student)
        self.stackedWidget.addWidget(self.streak_and_goals)
        self.stackedWidget.addWidget(self.manage_class)
        self.stackedWidget.addWidget(self.manage_homework)
        self.stackedWidget.addWidget(self.student_statistics)
        self.stackedWidget.addWidget(self.teacher_statistics)

        # Set the controller for each page
        self.home_page.setController(self)
        self.signup_page.setController(self)
        self.login_page.setController(self)
        self.student_dashboard.setController(self)
        self.teacher_dashboard.setController(self)
        self.choose_notes.setController(self)
        self.choose_question_topic.setController(self)
        self.answer_questions.setController(self)
        self.manage_account_details.setController(self)
        self.view_classes_student.setController(self)
        self.view_homework_student.setController(self)
        self.streak_and_goals.setController(self)
        self.manage_class.setController(self)
        self.manage_homework.setController(self)
        self.student_statistics.setController(self)
        self.teacher_statistics.setController(self)

        # Controllers for other classes
        self.user = None # Set reference to this in separate function
    
    def handlePageChange(self, nameForIndex):
        # This will change the index to the relevant page when called
        # Setup a dictionary which will hold all the relevant keys
        pagesIndex = {
            "home": 0,
            "signup": 1,
            "login": 2,
            "studentDashboard": 3,
            "teacherDashboard": 4,
            "chooseNotes": 5,
            "chooseQuestionTopic": 6,
            "answerQuestions": 7,
            "manageAccountDetails": 8,
            "viewClassesStudent": 9,
            "viewHomeworkStudent": 10,
            "streakAndGoals": 11,
            "manageClass": 12,
            "manageHomework": 13,
            "studentStatistics": 14,
            "teacherStatistics": 15
        }
        if nameForIndex in pagesIndex:
            self.stackedWidget.setCurrentIndex(pagesIndex[nameForIndex])
    
    def database(self, query=None, parameter=None, queryType=None):
        # This function will handle query execution to the database.
        # It must check if the query requires parameters or not (ie for inserting statements because %s will be needed in the query and will have different execution methods)

        # Connect to the database using environment variables for security
        try:
            conn = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("POSTGRESQL_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME")
            )
            
            # Create cursor to execute the queries
            cur = conn.cursor()
            if parameter:
                cur.execute(query, parameter)
            else:
                cur.execute(query)
            
            # Check query type to see if fetching or changing the database
            if queryType == "fetchItems":
                result = cur.fetchall()
                return result
            elif queryType == "changeDatabase":
                conn.commit()
                return cur.rowcount
            
            # Close connection & cursor
            cur.close()
            conn.close()

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def createUserReference(self, firstName, surname, username, email, accountType):
        # Create relevant object & store in self.user (initiated in the constructor already)
        user = User(firstName, surname, username, email, accountType)
        self.user = user
        self.user.setController(self)

    def run(self):
        # Actually goes and runs the application by showing the stacked widget
        self.stackedWidget.show()
        self.show()
        self.handlePageChange("home") # Start on the home page

class User:
    def __init__(self, firstName, surname, username, email, accountType):
        self.user_id = None # User ID will be set when the user is created in the databaseS
        self.firstName = firstName
        self.surname = surname
        self.username = username
        self.email = email
        self.accountType = accountType

        # Leave password and salt as None for now, when creating a user account or logging in, these will be set to the hashed password values
        self.hashedPassword = None
        self.salt = None

        # Link to the controller so that database functions can be called. Set to None but will be changed in controller class
        self.controller = None

        # Other attributes can be added later on as needed
        self.loggedIn = False

    def setController(self, controller):
        # Function to set the controller for the user class so that database functions can be called
        self.controller = controller
    
    def checkUsernameUnique(self):
        # Function to check if the username is unique in the database
        if self.accountType == "student": # Create the right query for correct account type
            query = "SELECT username FROM student WHERE username = %s"
        else:
            query = "SELECT username FROM teacher WHERE username = %s"
        parameter = (self.username,)
        result = self.controller.database(query, parameter, "fetchItems") # Get items

        if result: # Check if a result was returned
            return False
        else:
            return True
    
    def checkEmailUnique(self):
        # Function to check if the email is unique in the database
        if self.accountType == "student":
            query = "SELECT emailaddress FROM student WHERE emailaddress = %s"
        else:
            query = "SELECT emailaddress FROM teacher WHERE emailaddress = %s"
        parameter = (self.email,)
        result = self.controller.database(query, parameter, "fetchItems") # Get items
        
        if result: # Check if a result was returned
            return False
        else:
            return True
        
    def checkUsernameIsValid(self):
        # Function to check if the username is valid based on certain criteria
        # SQL Injection Prevention not needed as PostgreSQL  will handle it
        # You learn something new everyday

        # Load harmful words from the badwords.txt file
        harmfulWordsList = []
        try:
            with open("program/badwords.txt", "r") as file:
                harmfulWordsList = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print("File Not Found - Check Skipped.")
            return False

        # Presence Check for Username - Does it exist?
        if self.username is not None and self.username != "":

            # Length Check for Username
            if len(self.username) >= 8 and len(self.username) <= 32:
                
                # Security Check for certain terms (consists of phrases found in a file of inappropriate content)
                if self.username.lower() not in harmfulWordsList:

                    # Format Check For Special Characters
                    specialChars = '''!"#$%&'()*+,-./:;<=>?@[]^_`{|}~ '''
                    if not(any(char in specialChars for char in self.username)):

                        # Uniqueness Test using username uniqueness function
                        if self.checkUsernameUnique() == True:
                            # If all conditions met, return True
                            return True
                        
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    
    def checkEmailIsValid(self):
        # Load harmful words from the badwords.txt file
        harmfulWordsList = []
        try:
            with open("program/badwords.txt", "r") as file:
                harmfulWordsList = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print("File Not Found - Check Skipped.")
            return False
        
        # Presence Check for Email - Does it exist?
        if self.email is not None and self.email != "":
            # Length Check for email
            if len(self.email) >= 10 and "@" in self.email and (".com" in self.email or ".co.uk" in self.email or ".org" in self.email or ".net" in self.email):
                
                # Security Check for certain terms (consists of phrases found in a file of inappropriate content)
                if not any(badword in self.email.lower() for badword in harmfulWordsList):

                    # Format Check For Special Characters
                    specialChars = '''!"#$%&'()*+,-/:;<=>?[]^_`{|}~ '''
                    requiredChars = "@."
                    if any(char in requiredChars for char in self.email) and not(any(char in specialChars for char in self.email)):

                        # Uniqueness Test using username uniqueness function
                        if self.checkEmailUnique() == True:
                            # If all conditions met, return True
                            return True
                        else:
                            print("Failed 4")
                            return False
                    else:
                        print("Failed 3")
                        return False
                else:
                    print("Failed 2")
                    return False
            else:
                print("Failed 1")
                return False
        else:
            print("Failed 0")
            return False
    
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
            
    def generateHashedPassword(self, password):
        # Function to generate a hashed password and salt for the user
        # Password is now a parameter rather than an attribute of the class for security reasons
        # Salt is generated using os.urandom(16) which creates a random 16 byte string if no salt is provided
        # Uses Blake2b as a hashing algorithm
        # 100,000 iterations of the hash prevents brute force attacks
        # 64 byte length for the hash

        salt = os.urandom(16)

        hash = hashlib.pbkdf2_hmac("blake2b", password.encode('utf-8'), salt, iterations=100000, dklen=64)

        return (hash.hex(), salt.hex())


if __name__ == "__main__":
    # Load up the program
    app = QApplication(sys.argv)
    controller = Controller()

    controller.run()
    sys.exit(app.exec())