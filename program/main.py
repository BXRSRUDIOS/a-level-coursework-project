# Import relevant modules
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6 import uic

# Import Classes for all the different pages
from homePage import HomePage
from signUpPage import SignUpPage
from loginPage import LoginPage

class Controller(QMainWindow):
    def __init__(self):
        super().__init__()
        # Setup the actual stacked widget, this will hold the different pages to select and change to when relevant
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)

        self.currentPageIndex = 0

        # This should create object instances for all of the different pages
        self.home_page = HomePage()
        self.signup_page = SignUpPage()
        self.login_page = LoginPage()

        # Add pages to the stack
        self.stackedWidget.addWidget(self.home_page)    # Index 0 of the stacked widget
        self.stackedWidget.addWidget(self.signup_page)
        self.stackedWidget.addWidget(self.login_page)

        # Set the controller for each page
        self.home_page.setController(self)
        self.signup_page.setController(self)
        self.login_page.setController(self)
    
    def handlePageChange(self, nameForIndex):
        # This will change the index to the relevant page when called
        # Setup a dictionary which will hold all the relevant keys
        pagesIndex = {
            "home": 0,
            "signup": 1,
            "login": 2
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