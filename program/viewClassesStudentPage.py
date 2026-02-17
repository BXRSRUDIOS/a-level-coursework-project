import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QTableWidgetItem
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions
from datetime import date

class ViewClassesStudent(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/viewClassesStudentPage.ui", self)
        self.setWindowTitle("View Classes Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard"))
        self.refreshClassListButton.clicked.connect(lambda: self.updateClasses())

        self.logoutAccount.clicked.connect(lambda: self.logout())

        # Class List Dictionary to store class information
        # Store as {class_name: [class_id, hasHomework]}
        self.classList = {}

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
    def updateClasses(self):
        # Set row position to 0
        self.classTable.setRowCount(0)

        # Get class information from database
        classes = self.controller.database("""SELECT classes.id, classes.name, classes.year
                                           FROM classes
                                           JOIN class_student ON classes.id = class_student.class_id
                                           WHERE class_student.student_id = %s""", parameter=(self.controller.user.user_id,), queryType="fetchItems")
        
        # Get homework information from database
        homework = self.controller.database("""SELECT homework.id, homework.name, homework.dueDate, classes.name
                                            FROM homework
                                            JOIN class_homework ON homework.id = class_homework.homework_id
                                            JOIN classes ON class_homework.class_id = classes.id
                                            JOIN class_student ON classes.id = class_student.class_id
                                            WHERE class_student.student_id = %s""", parameter=(self.controller.user.user_id,), queryType="fetchItems")
        
        for item in homework:
            # Begin updating class list dictionary with class information
            className = item[3]
            if className not in self.classList:
                self.classList[className] = [item[0], True]
            else:
                self.classList[className][1] = True
        
        # Any classes with no homework will need false value
        for item in classes:
            className = item[1]
            if className not in self.classList:
                self.classList[className] = [item[0], False]
        
        for item in classes:
            # Get teacher username for the class
            teacherUsername = self.controller.database("""SELECT teacher.username
                                                        FROM teacher
                                                        JOIN class_teacher ON teacher.id = class_teacher.teacher_id
                                                        JOIN classes ON class_teacher.class_id = classes.id
                                                        WHERE classes.id = %s""", parameter=(item[0],), queryType="fetchItems")
            # Extract the username from the result (fetchItems returns a list of tuples)
            username = teacherUsername[0][0] if teacherUsername else "Unknown"
            
            # Update the table with the class information
            rowPosition = self.classTable.rowCount()
            self.classTable.insertRow(rowPosition)
            self.classTable.setItem(rowPosition, 0, QTableWidgetItem(item[1]))
            self.classTable.setItem(rowPosition, 1, QTableWidgetItem(str(item[2])))
            self.classTable.setItem(rowPosition, 2, QTableWidgetItem(username))
            if self.classList[item[1]][1] == True:
                self.classTable.setItem(rowPosition, 3, QTableWidgetItem("Yes"))
            else:
                self.classTable.setItem(rowPosition, 3, QTableWidgetItem("No"))
