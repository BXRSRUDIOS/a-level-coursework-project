from PyQt6.QtWidgets import QMessageBox

# General Exceptions Error Handling
def handle_exceptions(func):
    def wrapper(self, *args, **kwargs): # Take the function & original parameters (args & kwargs handle parameter handling)
        try:
            # Try to execute the original function
            return func(self, *args, **kwargs)
        except Exception as e:
            # Handle exceptions by showing a popup
            # Initialise Error Popup Messages with Relevant Information
            dialogueBox = QMessageBox()
            dialogueBox.setText(str(e))
            dialogueBox.setWindowTitle("System Error")
            dialogueBox.setIcon(QMessageBox.Icon.Critical)

            dialogueBox.exec()
            print(e)
    return wrapper