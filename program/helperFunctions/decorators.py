from PyQt6.QtWidgets import QMessageBox
import traceback

# General Exceptions Error Handling
def handle_exceptions(func):
    def wrapper(self, *args, **kwargs): # Take the function & original parameters (args & kwargs handle parameter handling)
        try:
            # Try to execute the original function
            return func(self, *args, **kwargs)
        except Exception as e:
            # Handle exceptions by showing a popup
            # Get the full traceback
            error_details = traceback.format_exc()

            # Initialise Error Popup Messages with Relevant Information
            dialogueBox = QMessageBox()
            dialogueBox.setText(error_details)
            dialogueBox.setWindowTitle("System Error")
            dialogueBox.setIcon(QMessageBox.Icon.Critical)

            dialogueBox.exec()
            print(error_details)
    return wrapper