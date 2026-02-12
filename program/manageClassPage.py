import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QTableWidgetItem, QComboBox
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
        self.modifyClassButton.clicked.connect(lambda: self.modifyClass())
        self.removeClassButton.clicked.connect(lambda: self.removeClass())
        self.addStudentButton.clicked.connect(lambda: self.addStudent())
        self.refreshStudentListButton.clicked.connect(lambda: self.refreshStudentList())
        self.removeStudentButton.clicked.connect(lambda: self.removeStudent())

        # Class List Dictionary to store class information
        # Store as {class_name: class_id}
        self.classList = {}

        # Class List Dictionary to store class information
        # Store as {student_name: student_id}
        self.studentList = {}
        
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

        self.refreshClassList()

    @handle_exceptions
    def refreshClassList(self):
        self.classesTable.setRowCount(0)  # Clear existing rows
        # Clear combo box before repopulating
        self.chooseClassComboBox.clear()
        self.chooseClassComboBox_2.clear()
        self.removeClassComboBox.clear()
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
            rowPosition = self.classesTable.rowCount()
            self.classesTable.insertRow(rowPosition)
            self.classesTable.setItem(rowPosition, 0, QTableWidgetItem(str(className)))
            self.classesTable.setItem(rowPosition, 1, QTableWidgetItem(str(classYear)))
            
            # Add to combo box
            display_text = f"{className} (Year {classYear})"
            self.chooseClassComboBox.addItem(display_text)
            self.removeClassComboBox.addItem(display_text)
            self.chooseClassComboBox_2.addItem(display_text)

            # Update the class list dictionary
            self.classList[display_text] = classId
    
    @handle_exceptions
    def modifyClass(self):
        # Get selected class from combo box
        selectedClass = self.chooseClassComboBox.currentText()
        if selectedClass not in self.classList:
            # Show error message if no class is selected
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Selection Error")
            dialogueBox.setText("No class selected. Please select a class to modify.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        else:
            # Get new class information from input fields
            classId = self.classList[selectedClass]
            newClassName = self.renameClassNameLineEdit.text()
            newClassYear = self.changeYearGroupSpinBox.value()

            # Check teacher has not created a class with the same name before, different teachers can use the same class name but one teacher cannot create two classes with the same name
            existingClasses = self.controller.database(query="""SELECT classes.id 
                                                       FROM classes 
                                                       JOIN class_teacher ON classes.id = class_teacher.class_id 
                                                       WHERE classes.name = %s AND class_teacher.teacher_id = %s;""", 
                                                       parameter=(newClassName, self.controller.user.user_id), 
                                                       queryType="fetchItems")
            if existingClasses:
                # Show error message if class with same name already exists for this teacher
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Input Error")
                dialogueBox.setText(f"You have already created a class named '{newClassName}'. Please choose a different name.")
                dialogueBox.setIcon(QMessageBox.Icon.Warning)
                dialogueBox.exec()
                return

            if not(newClassName):
                # Show error message if class name is empty
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Input Error")
                dialogueBox.setText("Class name cannot be empty.")
                dialogueBox.setIcon(QMessageBox.Icon.Warning)
                dialogueBox.exec()
                return None
            else:
                # Update class information in the database
                self.controller.database(query="UPDATE classes SET name = %s, year = %s WHERE id = %s;", parameter=(newClassName, newClassYear, classId), queryType="changeDatabase")

                # Show success message
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Class Modified")
                dialogueBox.setText(f"Class has been successfully modified to '{newClassName}' for Year {newClassYear}.")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.exec()
        
        self.refreshClassList()

    @handle_exceptions
    def removeClass(self):
        # Get selected class from combo box
        selectedClass = self.removeClassComboBox.currentText()
        if selectedClass not in self.classList:
            # Show error message if no class is selected
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Selection Error")
            dialogueBox.setText("No class selected. Please select a class to remove.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
            return None
        
        else:
            # Get class ID from the dictionary
            classId = self.classList[selectedClass]

            # Remove the class from the database
            self.controller.database(query="DELETE FROM class_teacher WHERE class_id = %s;", parameter=(classId,), queryType="changeDatabase")
            self.controller.database(query="DELETE FROM class_homework WHERE class_id = %s;", parameter=(classId,), queryType="changeDatabase")
            self.controller.database(query="DELETE FROM class_student WHERE class_id = %s;", parameter=(classId,), queryType="changeDatabase")
            self.controller.database(query="DELETE FROM classes WHERE id = %s;", parameter=(classId,), queryType="changeDatabase")

            # Show success message
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Class Removed")
            dialogueBox.setText(f"Class '{selectedClass}' and all data associated to it has been successfully removed.")
            dialogueBox.setIcon(QMessageBox.Icon.Information)
            dialogueBox.exec()

        self.refreshClassList()

    @handle_exceptions
    def clearClassList(self):
        self.classesTable.setRowCount(0)  # Clear existing rows
        # Also clear the class selection combo box if presents
        self.chooseClassComboBox.clear()
        self.removeClassComboBox.clear()
        self.chooseClassComboBox_2.clear()
        # Clear Class Dictionary 
        self.classList.clear()

    @handle_exceptions
    def findStudentExists(self, username, email):
        # Get the result from the database to then use to check student existance
        result = self.controller.database(query="SELECT id FROM student WHERE username = %s AND emailaddress = %s;", parameter=(username, email,), queryType="fetchItems")
        if result:
            return result  # Return the student ID and user information if found
        else:
            return False  # Return None if no student is found with the given username
    
    @handle_exceptions
    def addStudent(self):
        # Take in user input and find if the student exists
        username = self.enterUsernameLineEdit.text()
        email = self.enterEmailLineEdit.text()
        studentInfo = self.findStudentExists(username, email)
        
        if studentInfo:
            if self.chooseClassComboBox_2.currentText() == "":
            # Combo box is empty or has empty text
                self.refreshClassList()  # Refresh class list to ensure the class list dictionary is up to date

            classId = self.classList[self.chooseClassComboBox_2.currentText()]  # Get the class ID from the class list dictionary
            studentId = studentInfo[0][0]  # Get the student ID from the result of findStudentExists function
            
            if self.controller.database(query="SELECT * FROM class_student WHERE class_id = %s AND student_id = %s;", parameter=(classId, studentId), queryType="fetchItems"):
                # Show error message if student is already in the class
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Student Already Added")
                dialogueBox.setText(f"Student '{username}' is already added to the class.")
                dialogueBox.setIcon(QMessageBox.Icon.Warning)
                dialogueBox.exec()
                return None
            else:

               # Add the student to the class in the database
                self.controller.database(query="INSERT INTO class_student (class_id, student_id) VALUES (%s, %s);", parameter=(classId, studentId), queryType="changeDatabase")

                self.refreshStudentList()  # Refresh the student list to show the newly added student

                # Popup to show success message
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("Student Added")
                dialogueBox.setText(f"Student '{username}' has been added to the class.")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.exec()

        else:
            # Show error message if no student is found with the given username and email
            dialogueBox = QMessageBox()
            dialogueBox.setWindowTitle("Student Not Found")
            dialogueBox.setText("No student found with the given username and email. Please check the information and try again.")
            dialogueBox.setIcon(QMessageBox.Icon.Warning)
            dialogueBox.exec()
    
    @handle_exceptions
    def refreshStudentList(self):
        if self.chooseClassComboBox_2.currentText() == "":
            # Combo box is empty or has empty text
            self.refreshClassList()  # Refresh class list to ensure the class list dictionary is up to date

        self.studentsTable.setRowCount(0)  # Clear existing rows
        self.studentList.clear()  # Clear student list dictionary
        self.chooseStudentComboBox.clear()  # Clear student selection combo box before repopulating
        
        classId = self.classList[self.chooseClassComboBox_2.currentText()]  # Get the class ID from the class list dictionary

        # Fetch classes associated with the teacher
        students = self.controller.database(query="""SELECT student.id, student.username, student.firstname, student.surname, student.emailaddress
                                                    FROM student
                                                    JOIN class_student ON student.id = class_student.student_id 
                                                    WHERE class_student.class_id = %s;""", 
                                                    parameter=(classId,), 
                                                    queryType="fetchItems")
            
        # Populate the table and the combo box with the fetched classes
        for studentId, username, firstname, surname, emailaddress in students:
            # Get display information
            displayName = f"{firstname} {surname}"
            displayUsername = f"{username}"
            displayEmail = f"{emailaddress}"

            # Add to Table
            rowPosition = self.studentsTable.rowCount()
            self.studentsTable.insertRow(rowPosition)
            self.studentsTable.setItem(rowPosition, 0, QTableWidgetItem(str(displayName)))
            self.studentsTable.setItem(rowPosition, 1, QTableWidgetItem(str(displayUsername)))
            self.studentsTable.setItem(rowPosition, 2, QTableWidgetItem(str(displayEmail)))

            # Add to combo box
            self.chooseStudentComboBox.addItem(displayUsername)

            # Update the student list dictionary
            self.studentList[username] = studentId
    
    @handle_exceptions
    def removeStudent(self):
        # Get class and student IDs from dictionaries based on combo box selections
        classId = self.classList[self.chooseClassComboBox_2.currentText()]
        studentId = self.studentList[self.chooseStudentComboBox.currentText()]
        # Remove the student from the class in the database
        self.controller.database(query="DELETE FROM class_student WHERE class_id = %s AND student_id = %s;", parameter=(classId, studentId), queryType="changeDatabase")

        # Popup to show success message
        dialogueBox = QMessageBox()
        dialogueBox.setWindowTitle("Student Removed")
        dialogueBox.setText(f"Student '{self.chooseStudentComboBox.currentText()}' has been removed from the class.")
        dialogueBox.setIcon(QMessageBox.Icon.Information)
        dialogueBox.exec()

        self.refreshStudentList()  # Refresh the student list to show the removed student