import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions
import random

class AnswerQuestions(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/answerQuestionPage.ui", self)
        self.setWindowTitle("Answer Questions Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.returnToDashboardFunction())
        self.submitAnswer.clicked.connect(lambda: self.outputFeedback())
        self.nextQuestion.clicked.connect(lambda: self.nextQuestionFunction())
        

        self.logoutAccount.clicked.connect(lambda: self.logout())

        # Set up ID stores to receive from homework page
        self.classID = None
        self.homeworkID = None

        # Setuo a Question Dictionary to store question information
        """
        Store as follows:
        {
            question_number: {
                    "id": question_id,
                    "question": question_text,
                    "correctAnswer": correct_answer,
                    "incorrectAnswers": [incorrect_answer_a, incorrect_answer_b, incorrect_answer_c],
                    "difficulty": difficulty,
                    "topicCode": topic_code,
                    "feedback": feedback,
                    "status": "unanswered" or "correct" or "incorrect"
                }
        }
        """
        self.questionDict = {}

        # Other Relevant Information
        self.currentQuestion = 0
        self.totalQuestions = None
        self.questionText.setWordWrap(True) # Set word wrap for question text
        self.taskType = None # Either Homework or Topic 

    @handle_exceptions
    def returnToDashboardFunction(self):
        if self.currentQuestion < self.numberOfQuestions - 1:
            # Show confirmation dialog if user tries to return to dashboard before completing homework
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Confirm Return")
            dialogueBox.setText("You have not completed the task yet. Are you sure you want to return to the dashboard? Your progress will not be saved.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            response = dialogueBox.exec()

            if response == QMessageBox.StandardButton.No:
                return None
        self.controller.handlePageChange("studentDashboard")

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
    def test(self):
        print(self.classID, self.homeworkID)
    
    @handle_exceptions
    def fillUpQuestionDict(self, questions=None):
        if self.taskType == "Homework":
            self.currentQuestion = 0
            self.questionDict = {}
            # Get question information from database and fill up the question dictionary
            query = """SELECT question.id, question.questionName, question.correctAnswer, question.incorrectAnswerA, question.incorrectAnswerB, question.incorrectAnswerC, question.difficulty, question.topicCode, question.feedback
                        FROM question
                        JOIN question_homework ON question.id = question_homework.question_id
                        WHERE question_homework.homework_id = %s;"""
            results = self.controller.database(query=query, parameter=(self.homeworkID,), queryType="fetchItems") # Gets the data from database
        else:
            self.currentQuestion = 0
            self.questionDict = {}
            results = questions
        self.numberOfQuestions = len(results) # Used later for end of homework handling
            
        for index, result in enumerate(results):
            # Iterate through results and fill question dictionary
            self.questionDict[index] = {
                "id": result[0],
                "question": result[1],
                "correctAnswer": result[2],
                "incorrectAnswers": [result[3], result[4], result[5]],
                "difficulty": result[6],
                "topicCode": result[7],
                "feedback": result[8],
                "status": "unanswered"
            }
        #print(self.questionDict) # Testing purposes
    
    @handle_exceptions
    def populateAnswerUI(self):
        # Populate UI with question info depends on current index number
        qIndex = self.currentQuestion
        answers = self.questionDict[qIndex]["incorrectAnswers"] + [self.questionDict[qIndex]["correctAnswer"]]
        # incorporate random shuffle order
        random.shuffle(answers)

        # Set question text
        self.questionText.setText(self.questionDict[qIndex]["question"])
        # Set Text For Radio Buttons
        self.answer1.setText(answers[0])
        self.answer2.setText(answers[1])
        self.answer3.setText(answers[2])
        self.answer4.setText(answers[3])

        # Set topic code text
        topicCode = f"Topic: {self.questionDict[qIndex]['topicCode']}"
        self.topicText.setText(topicCode)
        # Set difficulty text
        self.difficultyText.setText(f"Difficulty: {self.questionDict[qIndex]['difficulty']}")
        # Clear radio button selection. Temporarily disable autoExclusive
        # so we can uncheck all radio buttons in the group.
        for btn in (self.answer1, self.answer2, self.answer3, self.answer4):
            btn.setAutoExclusive(False)
            btn.setChecked(False)
        for btn in (self.answer1, self.answer2, self.answer3, self.answer4):
            btn.setAutoExclusive(True)

        self.submitAnswer.setEnabled(True) # Enable submit answer button in case it was disabled from previous question
        self.nextQuestion.setEnabled(False) # Disable next question button until user has submitted an answer

        self.textBrowser.setText(f"Feedback:")
        self.textBrowser.setFontPointSize(14)

    @handle_exceptions
    def outputFeedback(self):
        # This should check if question correct and output feedback 
        # Take user input 
        if self.answer1.isChecked():
            selectedAnswer = self.answer1.text()
        elif self.answer2.isChecked():
            selectedAnswer = self.answer2.text()
        elif self.answer3.isChecked():
            selectedAnswer = self.answer3.text()
        elif self.answer4.isChecked():
            selectedAnswer = self.answer4.text()
        else:
            # No answer selected, show error message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Answer Selected")
            dialogueBox.setText("Please select an answer before submitting.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        correctAnswer = self.questionDict[self.currentQuestion]["correctAnswer"]
        feedback = self.questionDict[self.currentQuestion]["feedback"]
        if selectedAnswer == correctAnswer:
            # Answer is correct
            self.questionDict[self.currentQuestion]["status"] = "correct"
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Correct Answer")
            dialogueBox.setText(f"Correct! {feedback}")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()
        else:
            # Answer is incorrect
            self.questionDict[self.currentQuestion]["status"] = "incorrect"
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Incorrect Answer")
            dialogueBox.setText(f"Incorrect. The correct answer was: {correctAnswer}. {feedback}")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
        self.textBrowser.setText(f"Correct Answer: {correctAnswer}\n\nYour Answer: {selectedAnswer}\n\nFeedback: {feedback}")
        self.textBrowser.setFontPointSize(14)
        self.submitAnswer.setEnabled(False) # Disable submit answer button to prevent multiple submissions for same question
        self.nextQuestion.setEnabled(True) # Enable next question button to allow user to move on to next question
    
    @handle_exceptions
    def nextQuestionFunction(self):
        if self.currentQuestion == self.numberOfQuestions - 1:
            # End of task, show results
            correctAnswers = sum(1 for q in self.questionDict.values() if q["status"] == "correct")
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Task Completed")
            dialogueBox.setText(f"You have completed the task! Your score is {correctAnswers} out of {self.numberOfQuestions}. Saving To Statistics Now...")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()
            self.checkTaskType() # Update statistics based on task type
            self.controller.handlePageChange("studentDashboard") # Return to dashboard after completing homework
        else:
            self.currentQuestion += 1
            self.populateAnswerUI()
    
    @handle_exceptions
    def checkTaskType(self):
        if self.taskType == "Homework":
            self.generalStatistics() 
            self.homeworkStatistics()
            self.topicStatistics()
        else:
            self.generalStatistics()
            self.topicStatistics()

    @handle_exceptions
    def generalStatistics(self):
        # Called at the end of task
        correctAnswers = sum(1 for q in self.questionDict.values() if q["status"] == "correct")
        # Grab number of questions
        totalQuestions = self.numberOfQuestions
        # Grab stats from database for user
        results = self.controller.database(query="""SELECT statistic.noQuestionsAnswered, statistic.noCorrectQuestions
                                           FROM statistic
                                           WHERE statistic.student_id = %s;""", parameter=(self.controller.user.user_id,), queryType="fetchItems")
        # Add new results to old results
        noQuestionsAnswered = results[0][0] + totalQuestions
        noCorrectQuestions = results[0][1] + correctAnswers
        # Update stats in database
        self.controller.database(query="""UPDATE statistic
                                           SET noQuestionsAnswered = %s, noCorrectQuestions = %s
                                           WHERE statistic.student_id = %s;""", 
                                           parameter=(noQuestionsAnswered, noCorrectQuestions, self.controller.user.user_id), 
                                           queryType="changeDatabase")
        self.controller.streak_and_goals.updateNumberOfQuestionsGoal(totalQuestions)
        
    @handle_exceptions
    def homeworkStatistics(self):
        # Called at end of homework
        # Grab homework statistics from database for user and homework
        numHomeworksCompleted = self.controller.database(query="""SELECT statistic.noHomeworksCompleted
                                           FROM statistic
                                           WHERE statistic.student_id = %s;""", 
                                           parameter=(self.controller.user.user_id,), queryType="fetchItems")
        # Add new homework to old homework count
        numHomeworksCompleted = numHomeworksCompleted[0][0] + 1
        # Update homework count in database
        self.controller.database(query="""UPDATE statistic
                                           SET noHomeworksCompleted = %s
                                           WHERE statistic.student_id = %s;""", 
                                           parameter=(numHomeworksCompleted, self.controller.user.user_id), 
                                           queryType="changeDatabase")
        self.controller.streak_and_goals.updateHomeworkGoal()
        
        # Grab homework total questions & correct questions
        correctAnswers = sum(1 for q in self.questionDict.values() if q["status"] == "correct")
        totalQuestions = self.numberOfQuestions
        # Insert homework questions answered and correct in database
        self.controller.database(query="""INSERT INTO homework_accuracy (homework_id, noQuestionsHomeworkAnswered, noCorrectHomeworkQuestions)
                                             VALUES (%s, %s, %s);""", 
                                             parameter=(self.homeworkID, totalQuestions, correctAnswers), 
                                             queryType="changeDatabase")
        # Get homework statistics ID
        homeworkStatsId = self.controller.database(query="""SELECT id FROM homework_accuracy
                                                            WHERE homework_id = %s AND noQuestionsHomeworkAnswered = %s AND noCorrectHomeworkQuestions = %s
                                                            ORDER BY id DESC LIMIT 1;""", 
                                                            parameter=(self.homeworkID, totalQuestions, correctAnswers), 
                                                            queryType="fetchItems")[0][0]
        
        # Grab statistics ID for user
        statisticId = self.controller.database(query="""SELECT id FROM statistic
                                                        WHERE student_id = %s;""", 
                                                        parameter=(self.controller.user.user_id,), 
                                                        queryType="fetchItems")[0][0]

        # Link homework statistics to user in database
        self.controller.database(query="""INSERT INTO statistic_homework_accuracy (statistic_id, homework_accuracy_id)
                                             VALUES (%s, %s);""", 
                                             parameter=(statisticId, homeworkStatsId), 
                                             queryType="changeDatabase")
    
    @handle_exceptions
    def topicStatistics(self):
        """
        Design the questionChecker as follows

        questionChecker = {
            "1.1": {
                "questionsAnswered": 0,
                "correctQuestions": 0
            },
            "1.2": {
                "questionsAnswered": 0,
                "correctQuestions": 0
            },
        }
        etc
        """
        questionChecker = {}
        for q in self.questionDict.values():
            topicCode = q["topicCode"]
            if topicCode not in questionChecker:
                questionChecker[topicCode] = {
                    "topicCode": topicCode,
                    "questionsAnswered": 0,
                    "correctQuestions": 0
                }
            questionChecker[topicCode]["questionsAnswered"] += 1
            if q["status"] == "correct":
                questionChecker[topicCode]["correctQuestions"] += 1
        #print(questionChecker) # Testing purposes
        # Now we have the question checker filled out with the relevant information, we can update the database
        for topic in questionChecker.values():
            statisticId = self.controller.database(query="""SELECT id FROM statistic
                                                        WHERE student_id = %s;""", 
                                                        parameter=(self.controller.user.user_id,), 
                                                        queryType="fetchItems")[0][0]
            query1 = """SELECT sta.topic_accuracy_id FROM statistic_topic_accuracy sta JOIN topic_accuracy ta ON sta.topic_accuracy_id = ta.id WHERE sta.statistic_id = %s AND ta.topicCode = %s;"""
            topicAccuracyId = self.controller.database(query=query1, parameter=(statisticId, topic["topicCode"]), queryType="fetchItems")[0][0]

            query2 = "UPDATE topic_accuracy SET noQuestionsTopicAnswered = noQuestionsTopicAnswered + %s, noCorrectTopicQuestions = noCorrectTopicQuestions + %s WHERE id = %s;"
            self.controller.database(query=query2, parameter=(topic["questionsAnswered"], topic["correctQuestions"], topicAccuracyId), queryType="changeDatabase")
            