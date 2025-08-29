# Import relevant modules
import sys
import psycopg2
import os
import io
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic
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

    def run(self):
        # Actually goes and runs the application by showing the stacked widget
        self.stackedWidget.show()
        self.show()
        self.handlePageChange("home") # Start on the home page

class User:
    def __init__(self, user_id, firstName, surname, username, email, password, accountType):
        self.user_id = user_id
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

if __name__ == "__main__":
    # Load up the program
    app = QApplication(sys.argv)
    controller = Controller()
    controller.run()
    sys.exit(app.exec())