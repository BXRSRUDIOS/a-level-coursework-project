import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

class ChooseQuestionTopic(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/chooseQuestionTopicPage.ui", self)
        self.setWindowTitle("Choose Question Topic Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, this button will be its own function later on
        self.generateButton.clicked.connect(lambda: self.generateQuestions())
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
    def generateQuestions(self):
        # Get topic codes from checkboxes
        topics = []
        checked = False
        if self.topic1_1.isChecked():
            topics.append("1.1")
            checked = True
        if self.topic1_2.isChecked():
            topics.append("1.2")
            checked = True
        if self.topic1_3.isChecked():
            topics.append("1.3")
            checked = True
        if self.topic1_4.isChecked():
            topics.append("1.4")
            checked = True
        if self.topic1_5.isChecked():
            topics.append("1.5")
            checked = True
        if self.topic1_6.isChecked():
            topics.append("1.6")
            checked = True
        if self.topic2_1.isChecked():
            topics.append("2.1")
            checked = True
        if self.topic2_2.isChecked():
            topics.append("2.2")
            checked = True
        if self.topic2_3.isChecked():
            topics.append("2.3")
            checked = True
        if self.topic2_4.isChecked():
            topics.append("2.4")
            checked = True
        if self.topic2_5.isChecked():
            topics.append("2.5")
            checked = True
        
        if not checked:
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Topics Selected")
            dialogueBox.setText("Please select at least one topic to generate questions.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            numberQuestions = self.numberQuestionsGenerate.value() # Get the number of questions to generate from the spinbox
            difficulty = self.difficultyChoice.currentText() # Get the difficulty to generate from the dropdown
            questions = self.controller.generateQuestions(numberQuestions, difficulty, topics) # Get the generated questions from the controller function
            self.controller.handlePageChange("answerQuestions")
            self.controller.answer_questions.taskType = "Topic" 
            self.controller.answer_questions.fillUpQuestionDict(questions)
            self.controller.answer_questions.populateAnswerUI()
            
        