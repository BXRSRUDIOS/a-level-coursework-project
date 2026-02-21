from datetime import datetime, date, timedelta
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QTableWidgetItem
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions
import random

class StreakAndGoals(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/streakAndGoalsPage.ui", self)
        self.setWindowTitle("Streak & Goals Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, this button will be its own function later on
        self.refreshStreaksAndGoalsButton.clicked.connect(lambda: self.refreshStreakAndGoalsPage())
        self.logoutAccount.clicked.connect(lambda: self.logout())

    @handle_exceptions
    def logout(self):
        # Function to log the user out of their account
        # Create popup asking to confirm logout
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("Confirm Logout")
        dialogueBox.setText("Are you sure you want to log out of your account?")
        dialogueBox.setIcon(QMessageBox.Icon.Question)
        dialogueBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        response = dialogueBox.exec()

        if response == QMessageBox.StandardButton.No:
            return None
        else:
            # Reset all user attributes on logout
            #print(self.controller.user.user_id, self.controller.user.firstName, self.controller.user.surname, self.controller.user.username, self.controller.user.email, self.controller.user.accountType, self.controller.user.statistic_id, self.controller.user.hashedPassword, self.controller.user.salt, self.controller.user.loggedIn)
            self.controller.user.user_id = None 
            self.controller.user.firstName = None
            self.controller.user.surname = None
            self.controller.user.username = None
            self.controller.user.email = None
            self.controller.user.accountType = None
            self.controller.user.statistic_id = None
            self.controller.user.hashedPassword = None
            self.controller.user.salt = None
            self.controller.user.loggedIn = False
            self.controller.handlePageChange("home")
            self.controller.user = None

            # Show logout success message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Logged Out")
            dialogueBox.setText("You have been successfully logged out.")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()
    
    @handle_exceptions
    def setController(self, controller):
        # Function which will set the controller for the page. Will be called in main.py when initialising the pages into the stacked widgets
        self.controller = controller
        self.controller.userReferenceCreated.connect(self.updateUsernameLabel)
    
    @handle_exceptions
    def updateUsernameLabel(self, username):
        # Slot to update the username label
        self.username.setText(f"Hello, {username}")

    @handle_exceptions
    def updateStreak(self, status):
        # Update the streak 
        if status == True:
            self.controller.database("""UPDATE streaks
                                     SET numberDaysStreak = numberDaysStreak + 1
                                     WHERE student_id = %s""", parameter=(self.controller.user.user_id,), queryType="changeDatabase")
            currentStreak = self.controller.database("SELECT numberDaysStreak FROM streaks WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
            longestStreak = self.controller.database("SELECT longestDaysStreak FROM streaks WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        elif status == False:
            # Check if longest streak reached or surpassed and update longest streak if so, then reset current streak to 1
            # Get current streak & longest streak from database 
            currentStreak = self.controller.database("SELECT numberDaysStreak FROM streaks WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
            longestStreak = self.controller.database("SELECT longestDaysStreak FROM streaks WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]

        if currentStreak > longestStreak:
            self.controller.database("""UPDATE streaks
                                     SET longestDaysStreak = %s
                                     WHERE student_id = %s""", parameter=(currentStreak, self.controller.user.user_id), queryType="changeDatabase")
            if status == False and not (date.today() == self.controller.database("SELECT lastDayLoggedIn FROM login_statuses WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]):
                self.controller.database("""UPDATE streaks
                                        SET numberDaysStreak = 1
                                        WHERE student_id = %s""", parameter=(self.controller.user.user_id,), queryType="changeDatabase")
        
        # Set lastLoggedInToday to today's date
        today = date.today()
        self.controller.database("""UPDATE login_statuses
                                     SET lastDayLoggedIn = %s
                                     WHERE student_id = %s""", parameter=(today, self.controller.user.user_id), queryType="changeDatabase")
    
    @handle_exceptions
    def updateGoals(self):
        # Generate reset date as start of the week
        nextWeek = date.today() + timedelta(days=7)
        
        # Generate new weekly goals for the user
        numberOfLogins = random.randint(2,5)
        numberOfQuestions = random.randint(25,50)

        # Update database with new goals and reset progress
        query = """UPDATE goals
        SET timesLoggedIn = 0, questionsAnswered = 0, homeworksCompleted = 0, resetDate = %s,
        timesLoggedInTarget = %s, questionsAnsweredTarget = %s, homeworksCompletedTarget = 1
        WHERE student_id = %s"""
        parameters = (nextWeek, numberOfLogins, numberOfQuestions, self.controller.user.user_id)
        self.controller.database(query, parameter=parameters, queryType="changeDatabase")
    
    @handle_exceptions
    def updateNumberOfQuestionsGoal(self, questions):
        # Update the number of questions answered for the goals
        self.controller.database("""UPDATE goals
                                     SET questionsAnswered = questionsAnswered + %s
                                     WHERE student_id = %s""", parameter=(questions, self.controller.user.user_id), queryType="changeDatabase")
    
    @handle_exceptions
    def updateNumberOfLoginsGoal(self):
        # Update the number of times logged in for the goals
        self.controller.database("""UPDATE goals
                                     SET timesLoggedIn = timesLoggedIn + 1
                                     WHERE student_id = %s""", parameter=(self.controller.user.user_id,), queryType="changeDatabase")
    
    @handle_exceptions
    def updateHomeworkGoal(self):
        # Update the number of homeworks completed for the goals
        self.controller.database("""UPDATE goals
                                     SET homeworksCompleted = homeworksCompleted + 1
                                     WHERE student_id = %s""", parameter=(self.controller.user.user_id,), queryType="changeDatabase")
    
    @handle_exceptions
    def refreshStreakAndGoalsPage(self):
        # Get all the statistics from the database and update the labels on the streak and goals page
        # Get current streak and longest streak
        currentStreak = self.controller.database("SELECT numberDaysStreak FROM streaks WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        longestStreak = self.controller.database("SELECT longestDaysStreak FROM streaks WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        # Get date reset for goals
        goalResetDate = self.controller.database("SELECT resetDate FROM goals WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        # Get goals progress
        timesLoggedIn = self.controller.database("SELECT timesLoggedIn FROM goals WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        timesLoggedInTarget = self.controller.database("SELECT timesLoggedInTarget FROM goals WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        questionsAnswered = self.controller.database("SELECT questionsAnswered FROM goals WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        questionsAnsweredTarget = self.controller.database("SELECT questionsAnsweredTarget FROM goals WHERE student_id =%s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        homeworksCompleted = self.controller.database("SELECT homeworksCompleted FROM goals WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]
        homeworksCompletedTarget = self.controller.database("SELECT homeworksCompletedTarget FROM goals WHERE student_id = %s", parameter=(self.controller.user.user_id,), queryType="fetchItems")[0][0]

        # Update Table & Labels
        self.dateLabel.setText(f"Weekly Goals Reset Date: {goalResetDate}")
        self.stats.setItem(0,0, QTableWidgetItem(str(currentStreak)))
        self.stats.setItem(1,0, QTableWidgetItem(str(longestStreak)))
        self.stats.setItem(4,0, QTableWidgetItem(str(timesLoggedIn)))
        self.stats.setItem(4,1, QTableWidgetItem(str(timesLoggedInTarget)))
        self.stats.setItem(2,0, QTableWidgetItem(str(questionsAnswered)))
        self.stats.setItem(2,1, QTableWidgetItem(str(questionsAnsweredTarget)))
        self.stats.setItem(3,0, QTableWidgetItem(str(homeworksCompleted)))
        self.stats.setItem(3,1, QTableWidgetItem(str(homeworksCompletedTarget)))

