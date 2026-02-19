import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions
from datetime import date

class ViewHomeworkStudent(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/viewHomeworkStudentPage.ui", self)
        self.setWindowTitle("View Homework Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, this button will be its own function later on
        self.refreshClassButton.clicked.connect(lambda: self.refreshClassList())
        self.refreshHomeworkButton.clicked.connect(lambda: self.refreshHomeworkList())
        self.startHomeworkButton.clicked.connect(lambda: self.startHomework())

        self.logoutAccount.clicked.connect(lambda: self.logout())

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
        # Clear Class Dictionary 
        self.classList.clear()
        studentId = self.controller.user.user_id  # Get the student's user ID

        # Fetch classes associated with the student
        classes = self.controller.database(query="""SELECT classes.name, classes.year, classes.id
                                                    FROM classes 
                                                    JOIN class_student ON classes.id = class_student.class_id 
                                                    WHERE class_student.student_id = %s;""", 
                                                    parameter=(studentId,), 
                                                    queryType="fetchItems")
            
        # Populate the table and the combo box with the fetched classes
        for className, classYear, classId in classes:
            # Add to combo box
            display_text = f"{className} (Year {classYear})"
            self.chooseClassComboBox.addItem(display_text)

            # Update the class list dictionary
            self.classList[display_text] = classId
    
    @handle_exceptions
    def dueDateCheck(self, dueDate):
        # Make duedate into date object
        if dueDate is None:
            return False
        
        # Handle datetime objects & extract date
        if hasattr(dueDate, 'date'):
            dueDate = dueDate.date()
        # Handle string dates
        elif isinstance(dueDate, str):
            dueDate = date.fromisoformat(dueDate)

        # Check due date <= current date
        currentDate = date.today()
        if dueDate <= currentDate:
            return False
        else:
            return True
    
    @handle_exceptions
    def refreshHomeworkList(self):
        # Clear combo boxes
        self.chooseHomeworkTaskComboBox.clear()
        # Grab class ID from the combo box
        selectedClass = self.chooseClassComboBox.currentText()
        classId = self.classList.get(selectedClass)
        # Clear homework dictionary
        self.homeworkList.clear()
        
        if not classId:
            # Error message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Class Selected")
            dialogueBox.setText("Please select a class before refreshing the homework list.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        # Fetch homework associated with the selected class
        homework = self.controller.database(query="""SELECT homework.name, homework.id, homework.dueDate
                                                    FROM homework 
                                                    JOIN class_homework ON homework.id = class_homework.homework_id 
                                                    WHERE class_homework.class_id = %s;""", 
                                                    parameter=(classId,), 
                                                    queryType="fetchItems")
        for name, id, dueDate in homework:
            # Check if due date has passed
            if self.dueDateCheck(dueDate): # This function was taken from viewClassesStudentPage.py
                # Update homework list dictionary
                self.homeworkList[name] = id

                # Add names to combo boxes
                self.chooseHomeworkTaskComboBox.addItem(name)
        
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("All Homeworks Added")
        dialogueBox.setText("All homeworks have been added to the homework list. If there is no homework in the list, it is because all homeworks are past due date or the teacher hasn't set any yet.")
        dialogueBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialogueBox.setIcon(QMessageBox.Icon.Information)
        dialogueBox.exec()

    @handle_exceptions
    def startHomework(self):
        # Get homework ID
        selectedHomework = self.chooseHomeworkTaskComboBox.currentText()
        homeworkId = self.homeworkList.get(selectedHomework)

        if not homeworkId:
            # Error message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("No Homework Selected")
            dialogueBox.setText("Please select a homework task before starting the homework.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            self.controller.handlePageChange("answerQuestions")
            self.controller.answer_questions.classID = self.classList.get(self.chooseClassComboBox.currentText())
            self.controller.answer_questions.homeworkID = homeworkId
            self.controller.answer_questions.fillUpQuestionDict()
            self.controller.answer_questions.populateAnswerUI()
            self.controller.answer_questions.taskType = "Homework"
    
    