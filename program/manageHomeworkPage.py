import sys
from datetime import datetime, date
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QTableWidgetItem, QComboBox, QTabWidget
from PyQt6.QtCore import QDate
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

class ManageHomework(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/manageHomeworkPage.ui", self)
        self.setWindowTitle("Manage Homework Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("teacherDashboard"))
        self.refreshClassLists.clicked.connect(lambda: self.refreshClassList())
        self.createHomeworkButton.clicked.connect(lambda: self.createHomework())
        self.refreshHomeworkListButton.clicked.connect(lambda: self.refreshHomeworkList())
        self.modifyHomeworkButton.clicked.connect(lambda: self.modifyHomework())
        self.refreshQuestionListButton.clicked.connect(lambda: self.refreshQuestionList())
        self.genQuestionButton.clicked.connect(lambda: self.generateQuestions())
        self.addQuestionButton.clicked.connect(lambda: self.createCustomQuestion())
        self.removeQuestionButton.clicked.connect(lambda: self.deleteQuestion())
        self.deleteHomeworkButton.clicked.connect(lambda: self.deleteHomework())
        self.logoutAccount.clicked.connect(lambda: self.logout())

        # Add items to the difficulty combo box
        self.difficultyComboBox.addItem("Easy")
        self.difficultyComboBox.addItem("Medium")
        self.difficultyComboBox.addItem("Hard")

        self.difficultyComboBox_2.addItem("Easy")
        self.difficultyComboBox_2.addItem("Medium")
        self.difficultyComboBox_2.addItem("Hard")

        self.changeDifficultyComboBox.addItem("Easy")
        self.changeDifficultyComboBox.addItem("Medium")
        self.changeDifficultyComboBox.addItem("Hard")

        self.enterDifficultyComboBox.addItem("Easy")
        self.enterDifficultyComboBox.addItem("Medium")
        self.enterDifficultyComboBox.addItem("Hard")

        # Class List Dictionary to store class information
        # Store as {class_name: class_id}
        self.classList = {}

        # Homework List Dictionary to store homework information
        # Store as {homework_name: homework_id}
        self.homeworkList = {}

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
    def refreshClassList(self):
        # Clear combo box before repopulating
        self.chooseClassComboBox.clear()
        self.chooseClassComboBox_2.clear()
        self.chooseClassComboBox_4.clear()
        self.chooseClassComboBox_6.clear()
        # Clear Class Dictionary 
        self.classList.clear()
        teacherId = self.controller.user.user_id  # Get the teacher's user ID

        # Fetch classes associated with the teacher
        classes = self.controller.database(query="""SELECT classes.name, classes.year, classes.id
                                                    FROM classes 
                                                    JOIN class_teacher ON classes.id = class_teacher.class_id 
                                                    WHERE class_teacher.teacher_id = %s;""", 
                                                    parameter=(teacherId,), 
                                                    queryType="fetchItems")
            
        # Populate the table and the combo box with the fetched classes
        for className, classYear, classId in classes:
            # Add to combo box
            display_text = f"{className} (Year {classYear})"
            self.chooseClassComboBox.addItem(display_text)
            self.chooseClassComboBox_2.addItem(display_text)
            self.chooseClassComboBox_4.addItem(display_text)
            self.chooseClassComboBox_6.addItem(display_text)


            # Update the class list dictionary
            self.classList[display_text] = classId
    
    @handle_exceptions
    def getSelectedClassId(self, comboBox):
        # Get the selected class ID from a given combo box
        selectedClass = comboBox.currentText()
        return self.classList.get(selectedClass)
    
    @handle_exceptions
    def createHomework(self):
        # Get text inputs for creating homework
        classID = self.getSelectedClassId(self.chooseClassComboBox)
        name = self.homeworkNameLineEdit.text()
        difficulty = self.difficultyComboBox.currentText()
        
        # Data from date input needs to be turned into date object
        qDateObject = self.dueDateDateEdit.date()
        dueDate = date(qDateObject.year(), qDateObject.month(), qDateObject.day())

        # Ensure all fields are filled out
        if not name or not difficulty or not dueDate or not classID:
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Missing Information")
            dialogueBox.setText("Please fill out all fields to create homework.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None

        # Validate the date and ensure due date > current date
        currDate = date.today()
        if dueDate <= currDate:
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Due Date")
            dialogueBox.setText("The due date must be in the future. Please select a valid due date.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            # Insert homework into the database
            self.controller.database(query="""INSERT INTO homework (name, dueDate, difficulty) VALUES (%s, %s, %s);""", 
                                        parameter=(name, dueDate, difficulty), 
                                        queryType="changeDatabase")
            # Get ID of the homework created
            homeworkId = self.controller.database(query="""SELECT id FROM homework WHERE name = %s AND dueDate = %s AND difficulty = %s ORDER BY id DESC LIMIT 1;""", 
                                                    parameter=(name, dueDate, difficulty), 
                                                    queryType="fetchItems")[0][0]
            
            # Insert into class_homework table 
            self.controller.database(query="""INSERT INTO class_homework (class_id, homework_id) VALUES (%s, %s);""", 
                                        parameter=(classID, homeworkId), 
                                        queryType="changeDatabase")
            
            # Show success popup to confirm homework creation
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Homework Created")
            dialogueBox.setText("The homework has been successfully created.")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()

            # Refresh the homework list to show the newly created homework
            self.refreshHomeworkList()
    
    @handle_exceptions
    def refreshHomeworkList(self):
        # Clear combo boxes
        self.chooseHomeworkComboBox.clear()
        self.chooseHomeworkComboBox_2.clear()
        self.chooseHomeworkComboBox_4.clear()
        self.chooseHomeworkComboBox_6.clear()
        
        # Clear homeworkTable
        self.homeworkTable.setRowCount(0)

        # Clear homework dictionary
        self.homeworkList.clear()

        # Get the selected class ID from the combo box
        # Depends on tab index on QTabWidget
        currIndex = self.homeworkManagement.currentIndex()
        if currIndex == 0:
            classId = self.getSelectedClassId(self.chooseClassComboBox)
        elif currIndex == 1:
            classId = self.getSelectedClassId(self.chooseClassComboBox_2)
        elif currIndex == 2:
            classId = self.getSelectedClassId(self.chooseClassComboBox_4)
        elif currIndex == 3:
            classId = self.getSelectedClassId(self.chooseClassComboBox_6)
        else:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Tab Index")
            dialogueBox.setText("An error occurred while trying to refresh the homework list.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        if not classId:
            # Error message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Class Selected")
            dialogueBox.setText("Please select a class before refreshing the homework list.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        # Fetch homework associated with the selected class
        homework = self.controller.database(query="""SELECT homework.name, homework.id, homework.dueDate, homework.difficulty
                                                    FROM homework 
                                                    JOIN class_homework ON homework.id = class_homework.homework_id 
                                                    WHERE class_homework.class_id = %s;""", 
                                                    parameter=(classId,), 
                                                    queryType="fetchItems")
        for name, id, dueDate, difficulty in homework:
            # Update homework list dictionary
            self.homeworkList[name] = id

            # Add names to combo boxes
            self.chooseHomeworkComboBox.addItem(name)
            self.chooseHomeworkComboBox_2.addItem(name)
            self.chooseHomeworkComboBox_4.addItem(name)
            self.chooseHomeworkComboBox_6.addItem(name)

            # Add homework to the table
            rowPosition = self.homeworkTable.rowCount()
            self.homeworkTable.insertRow(rowPosition)
            self.homeworkTable.setItem(rowPosition, 0, QTableWidgetItem(name))
            self.homeworkTable.setItem(rowPosition, 1, QTableWidgetItem(str(dueDate)))
            self.homeworkTable.setItem(rowPosition, 2, QTableWidgetItem(difficulty))

    @handle_exceptions
    def getSelectedHomeworkId(self, comboBox):
        # Get the selected homework ID from a given combo box
        selectedHomework = comboBox.currentText()
        return self.homeworkList.get(selectedHomework)
    
    @handle_exceptions
    def modifyHomework(self):
        # Get the selected homework ID from the combo box
        homeworkId = self.getSelectedHomeworkId(self.chooseHomeworkComboBox)
        if not homeworkId:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework before modifying it.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None

        # Get the new values from the input fields
        name = self.renameHomeworkLineEdit.text()
        difficulty = self.changeDifficultyComboBox.currentText()

        # Data from date input needs to be turned into date object
        qDateObject = self.changeDueDateDateEdit.date()
        dueDate = date(qDateObject.year(), qDateObject.month(), qDateObject.day())
        
        # Ensure all fields are filled out
        if not name or not difficulty or not dueDate:
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Missing Information")
            dialogueBox.setText("Please fill out all fields to modify the homework.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        # Validate the date and ensure due date > current date
        currDate = date.today()
        if dueDate <= currDate:
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Due Date")
            dialogueBox.setText("The due date must be in the future. Please select a valid due date.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        

        # Update the homework in the database
        self.controller.database(query="""UPDATE homework SET name = %s, dueDate = %s, difficulty = %s WHERE id = %s;""", 
                                parameter=(name, str(dueDate), difficulty, homeworkId), queryType="changeDatabase")

        # Refresh the homework list to reflect changes
        self.refreshHomeworkList()

    @handle_exceptions
    def refreshQuestionList(self):
        # Clear questionTable
        self.questionTable.setRowCount(0)

        # Get the selected homework ID from the combo box
        homeworkId = self.getSelectedHomeworkId(self.chooseHomeworkComboBox_2)
        if not homeworkId:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework before refreshing the question list.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        # Fetch questions associated with the selected homework
        questions = self.controller.database(query="""SELECT question.id, question.questionName, question.correctAnswer, question.incorrectAnswerA, 
                                             question.incorrectAnswerB, question.incorrectAnswerC, question.difficulty, question.topicCode, question.feedback 
                                             FROM question
                                             JOIN question_homework 
                                             ON question.id = question_homework.question_id
                                             WHERE homework_id = %s;""", 
                                            parameter=(homeworkId,), 
                                            queryType="fetchItems")
        
        for id, questionName, correctAnswer, incorrectAnswerA, incorrectAnswerB, incorrectAnswerC, difficulty, topicCode, feedback in questions:
            # Add question to the table
            rowPosition = self.questionTable.rowCount()
            self.questionTable.insertRow(rowPosition)
            self.questionTable.setItem(rowPosition, 0, QTableWidgetItem(str(id)))
            self.questionTable.setItem(rowPosition, 1, QTableWidgetItem(questionName))
            self.questionTable.setItem(rowPosition, 2, QTableWidgetItem(correctAnswer))
            self.questionTable.setItem(rowPosition, 3, QTableWidgetItem(incorrectAnswerA))
            self.questionTable.setItem(rowPosition, 4, QTableWidgetItem(incorrectAnswerB))
            self.questionTable.setItem(rowPosition, 5, QTableWidgetItem(incorrectAnswerC))
            self.questionTable.setItem(rowPosition, 6, QTableWidgetItem(difficulty))
            self.questionTable.setItem(rowPosition, 7, QTableWidgetItem(topicCode))
            self.questionTable.setItem(rowPosition, 8, QTableWidgetItem(feedback))

    @handle_exceptions
    def generateQuestions(self):
        # Take in & validate inputs
        homeworkID = self.getSelectedHomeworkId(self.chooseHomeworkComboBox_4)
        numQuestions = self.numberOfQuestionsSpinBox.value()
        difficulty = self.difficultyComboBox_2.currentText()
        self.topic_checkboxes = {
            '1.1': self.topic1_1,
            '1.2': self.topic1_2,
            '1.3': self.topic1_3,
            '1.4': self.topic1_4,
            '1.5': self.topic1_5,
            '1.6': self.topic1_6,
            '2.1': self.topic2_1,
            '2.2': self.topic2_2,
            '2.3': self.topic2_3,
            '2.4': self.topic2_4,
            '2.5': self.topic2_5,
        }
        # Check which checkboxes are ticked
        selectedTopics = [topic for topic, checkbox in self.topic_checkboxes.items() if checkbox.isChecked()]

        if not homeworkID:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework before generating questions.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif numQuestions <= 0:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Number of Questions")
            dialogueBox.setText("Please select a valid number of questions to generate.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif not difficulty:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Difficulty Selected")
            dialogueBox.setText("Please select a difficulty level before generating questions.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif not selectedTopics:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Topics Selected")
            dialogueBox.setText("Please select at least one topic before generating questions.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            # Get results from function
            result = self.controller.generateQuestions(numQuestions, difficulty, selectedTopics)
            print(result) # Testing purposes

            # Clear existing questions
            self.controller.database(query="""DELETE FROM question_homework WHERE homework_id = %s;""", 
                                        parameter=(homeworkID,), 
                                        queryType="changeDatabase")

            # Store new ones in question_homework table
            for question in result:
                questionId = question[0]  # Extract the question ID (first column)
                self.controller.database(query="""INSERT INTO question_homework (question_id, homework_id) VALUES (%s, %s);""", 
                                            parameter=(questionId, homeworkID), 
                                            queryType="changeDatabase")

            self.refreshQuestionList()  # Refresh question table

            # Add popup to say questions generated successfully
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Generating Questions")
            dialogueBox.setText("Questions Generated Successfully!")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()
    
    @handle_exceptions
    def createCustomQuestion(self):
        homeworkID = self.getSelectedHomeworkId(self.chooseHomeworkComboBox_6)
        question = self.enterQuestionLineEdit.text()
        difficulty = self.enterDifficultyComboBox.currentText()
        self.topic_checkboxes = {
            '1.1': self.Topic1_1,
            '1.2': self.Topic1_2,
            '1.3': self.Topic1_3,
            '1.4': self.Topic1_4,
            '1.5': self.Topic1_5,
            '1.6': self.Topic1_6,
            '2.1': self.Topic2_1,
            '2.2': self.Topic2_2,
            '2.3': self.Topic2_3,
            '2.4': self.Topic2_4,
            '2.5': self.Topic2_5,
        }
        # Check which checkboxes are ticked
        selectedTopics = [topic for topic, checkbox in self.topic_checkboxes.items() if checkbox.isChecked()]

        correctAnswer = self.enterCorrectAnswerLineEdit.text()
        incorrectAnswerA = self.enterIncorrectAnswer1LineEdit.text()
        incorrectAnswerB = self.enterIncorrectAnswer2LineEdit.text()
        incorrectAnswerC = self.enterIncorrectAnswer3LineEdit.text()
        feedback = self.enterFeedbackLineEdit.toPlainText()

        if not homeworkID:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework before creating a custom question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif not difficulty:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Difficulty Selected")
            dialogueBox.setText("Please select a difficulty level before creating a custom question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif not question:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Question Entered")
            dialogueBox.setText("Please enter a question before creating a custom question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif len(selectedTopics) <= 0 or len(selectedTopics) > 1:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Invalid Number of Topics Selected")
            dialogueBox.setText("Please select exactly one topic before creating a custom question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif not correctAnswer or not incorrectAnswerA or not incorrectAnswerB or not incorrectAnswerC or not feedback:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Missing Information")
            dialogueBox.setText("Please fill in all answer-related fields before creating a custom question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:

            query = """INSERT INTO question (questionName, correctAnswer, incorrectAnswerA, incorrectAnswerB, incorrectAnswerC, difficulty, topicCode, feedback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
            parameter = (question, correctAnswer, incorrectAnswerA, incorrectAnswerB, incorrectAnswerC, difficulty, selectedTopics[0], feedback)
            self.controller.database(query=query, parameter=parameter, queryType="changeDatabase")

            # Get ID of the question created
            questionId = self.controller.database(query="""SELECT id FROM question WHERE questionName = %s AND correctAnswer = %s AND incorrectAnswerA = %s AND 
                                                        incorrectAnswerB = %s AND incorrectAnswerC = %s AND difficulty = %s AND topicCode = %s AND feedback = %s
                                                        ORDER BY id DESC LIMIT 1;""", 
                                                        parameter=parameter, 
                                                        queryType="fetchItems")[0][0]
            # Insert into question_homework table
            self.controller.database(query="""INSERT INTO question_homework (question_id, homework_id) VALUES (%s, %s);""", 
                                        parameter=(questionId, homeworkID), 
                                        queryType="changeDatabase")
            self.refreshQuestionList()  # Refresh question table
    
            # Add popup to say question created successfully
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Creating Custom Question")
            dialogueBox.setText("Custom Question Created Successfully!")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()
    
    @handle_exceptions
    def deleteQuestion(self):
        homeworkID = self.getSelectedHomeworkId(self.chooseHomeworkComboBox_2)
        questionId = int(self.removeQuestionEnter.text())

        if not homeworkID:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework before deleting a question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        elif not questionId:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Question ID Entered")
            dialogueBox.setText("Please enter a question ID before deleting a question.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            checkInHomework = self.controller.database(query="""SELECT * FROM question_homework WHERE question_id = %s and homework_id = %s;""", parameter=(questionId, homeworkID), queryType="fetchItems")
            if not checkInHomework:
                # Error message popup
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Invalid Question ID")
                dialogueBox.setText("The question ID entered is not associated with the selected homework. Please enter a valid question ID.")
                dialogueBox.setIcon(QMessageBox.Icon.Warning)
                dialogueBox.exec()
                return None
            else:
                # Delete question 
                self.controller.database(query="""DELETE FROM question_homework WHERE question_id = %s and homework_id = %s;""", parameter=(questionId, homeworkID), queryType="changeDatabase")
                self.refreshQuestionList()  # Refresh question table

                # Add popup to say question deleted successfully
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Deleting Question")
                dialogueBox.setText("Question Deleted Successfully!")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.exec()

    @handle_exceptions
    def deleteHomework(self):
        homeworkID = self.getSelectedHomeworkId(self.chooseHomeworkComboBox)

        if not homeworkID:
            # Error message popup
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework before deleting.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            # Delete homework from database
            self.controller.database(query="""DELETE FROM question_homework WHERE homework_id = %s;""", parameter=(homeworkID,), queryType="changeDatabase")
            self.controller.database(query="""DELETE FROM class_homework WHERE homework_id = %s;""", parameter=(homeworkID,), queryType="changeDatabase")
            self.controller.database(query="""DELETE FROM homework WHERE id = %s;""", parameter=(homeworkID,), queryType="changeDatabase")
            
            self.refreshHomeworkList()  # Refresh homework list to reflect deletion

            # Add popup to say homework deleted successfully
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Deleting Homework")
            dialogueBox.setText("Homework Deleted Successfully!")

