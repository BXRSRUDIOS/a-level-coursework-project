import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QTableWidgetItem
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

class ManageClass(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/manageClassPage.ui", self)
        self.setWindowTitle("Manage Class Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py

        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.returnToDashboardCode())

        # Connect logout button to logout function
        self.logoutAccount.clicked.connect(lambda: self.logout())
        
        # Connect Class Buttons to their respective functions
        self.createClassButton.clicked.connect(lambda: self.createClass())
        self.refreshClassLists.clicked.connect(lambda: self.refreshClassList())
        
    @handle_exceptions
    def returnToDashboardCode(self):
        # Function to return to the dashboard page
        self.controller.handlePageChange("teacherDashboard")
        self.clearClassList()

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

        # Clear Class List When Logging Out
        self.clearClassList()

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
    def createClass(self):
        # Get the information inputted by the user
        inputClassName = self.classNameLineEdit.text()
        inputClassYear = self.yearGroupSpinBox.value()

        if not inputClassName:
            # Show error message if class name is empty
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Input Error")
            dialogueBox.setText("Class name cannot be empty.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        else:
            # Check teacher has not created a class with the same name before, different teachers can use the same class name but one teacher cannot create two classes with the same name
            existingClasses = self.controller.database(query="""SELECT classes.id 
                                                       FROM classes 
                                                       JOIN class_teacher ON classes.id = class_teacher.class_id 
                                                       WHERE classes.name = %s AND class_teacher.teacher_id = %s;""", 
                                                       parameter=(inputClassName, self.controller.user.user_id), 
                                                       queryType="fetchItems")
            if existingClasses:
                # Show error message if class with same name already exists for this teacher
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Input Error")
                dialogueBox.setText(f"You have already created a class named '{inputClassName}'. Please choose a different name.")
                dialogueBox.setIcon(QMessageBox.Icon.Warning)
                dialogueBox.exec()
                return
            
            else:
                # Write new class to classes table
                self.controller.database(query="INSERT INTO classes (name, year) VALUES (%s, %s);", parameter=(inputClassName, inputClassYear), queryType="changeDatabase")

                # Write new to class_teacher table to link class to teacher
                teacherId = self.controller.user.user_id
                classId = self.controller.database(query="SELECT id FROM classes WHERE name = %s AND year = %s ORDER BY id DESC LIMIT 1;", parameter=(inputClassName, inputClassYear), queryType="fetchItems")[0]
                self.controller.database(query="INSERT INTO class_teacher (class_id, teacher_id) VALUES (%s, %s);", parameter=(classId, teacherId), queryType="changeDatabase")

                # Show success message
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Class Created")
                dialogueBox.setText(f"Class '{inputClassName}' for Year {inputClassYear} has been successfully created.")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.exec()

    @handle_exceptions
    def refreshClassList(self):
        self.classesTable.setRowCount(0)  # Clear existing rows
        teacherId = self.controller.user.user_id  # Get the teacher's user ID
            
        # Fetch classes associated with the teacher
        classes = self.controller.database(query="""SELECT classes.name, classes.year 
                                                    FROM classes 
                                                    JOIN class_teacher ON classes.id = class_teacher.class_id 
                                                    WHERE class_teacher.teacher_id = %s;""", 
                                                    parameter=(teacherId,), 
                                                    queryType="fetchItems")
            
        # Populate the table with the fetched classes
        for className, classYear in classes:
            rowPosition = self.classesTable.rowCount()
            self.classesTable.insertRow(rowPosition)
            self.classesTable.setItem(rowPosition, 0, QTableWidgetItem(str(className)))  # Ensure str
            self.classesTable.setItem(rowPosition, 1, QTableWidgetItem(str(classYear)))  # Ensure str
    
    def clearClassList(self):
        self.classesTable.setRowCount(0)  # Clear existing rows

