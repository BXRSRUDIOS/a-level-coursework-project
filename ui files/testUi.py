import PyQt6

# From homePage.ui import the ui file and make it viewable
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
import sys
import os
from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()
# Set the path to the UI file

files = {
    "1": "homePage.ui",
    "2": "signupPage.ui",
    "3": "loginPage.ui",
}

ui_file_path = os.path.join(os.path.dirname(__file__), files["3"])
# Load the UI file
class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(ui_file_path, self)
        self.setWindowTitle("Home Page")  # Set the window title
        #self.setGeometry(100, 100, 800, 800)

def main():
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()