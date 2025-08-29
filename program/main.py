# Import relevant modules
import sys
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
    
    def run(self):
        # Actually goes and runs the application by showing the stacked widget
        self.stackedWidget.show()
        self.show()
        self.handlePageChange("home") # Start on the home page

if __name__ == "__main__":
    # Load up the program
    app = QApplication(sys.argv)
    controller = Controller()
    controller.run()
    sys.exit(app.exec())