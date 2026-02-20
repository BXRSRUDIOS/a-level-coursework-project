import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QDialog, QVBoxLayout
from PyQt6 import uic
from helperFunctions.decorators import handle_exceptions

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np

class StudentStatistics(QMainWindow):
    def __init__(self):
        # Create the main window for the home page
        super().__init__()
        uic.loadUi("the project/ui files/studentStatisticsPage.ui", self)
        self.setWindowTitle("Your Statistics Page")
        
        # Create a link to the main controller 
        self.controller = None # All initialisations of the controller will be done in main.py
    
        # Connect button signals to their respective functions
        self.manageAccountDetails.clicked.connect(lambda: self.controller.handlePageChange("manageAccountDetails"))
        self.returnToDashboard.clicked.connect(lambda: self.controller.handlePageChange("studentDashboard")) # Temporary, this button will be its own function later on
        self.refreshStatisticsButton.clicked.connect(lambda: self.loadStatistics())
        self.loadTopicAccuracyButton.clicked.connect(lambda: self.loadTopicAccuracy())
        self.logoutAccount.clicked.connect(lambda: self.logout())
        self.graphStatisticsButton.clicked.connect(lambda: self.graphStatistics())

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
    def getQuestionStatistics(self):
        query = """SELECT statistic.id, statistic.noQuestionsAnswered, statistic.noCorrectQuestions
        FROM statistic
        WHERE statistic.student_id = %s;"""

        # Calculate accuracy for the topic
        results = self.controller.database(query=query, parameter=(self.controller.user.user_id,), queryType="fetchItems")
        numQuestionsAnswered = results[0][1]
        numCorrectQuestions = results[0][2]
        accuracy = (numCorrectQuestions / numQuestionsAnswered) * 100 if numQuestionsAnswered > 0 else 0
        return numQuestionsAnswered, numCorrectQuestions, accuracy
    
    @handle_exceptions
    def getTopicStatistics(self, topic):
        query = """SELECT topic_accuracy.id, topic_accuracy.noQuestionsTopicAnswered, topic_accuracy.noCorrectTopicQuestions
        FROM topic_accuracy
        JOIN statistic_topic_accuracy ON topic_accuracy.id = statistic_topic_accuracy.topic_accuracy_id
        JOIN statistic ON statistic_topic_accuracy.statistic_id = statistic.id
        WHERE statistic.student_id = %s AND topic_accuracy.topicCode = %s;"""

        # Calculate accuracy for the topic
        results = self.controller.database(query=query, parameter=(self.controller.user.user_id, topic), queryType="fetchItems")
        numQuestionsAnswered = results[0][1]
        numCorrectQuestions = results[0][2]
        accuracy = (numCorrectQuestions / numQuestionsAnswered) * 100 if numQuestionsAnswered > 0 else 0
        return numQuestionsAnswered, numCorrectQuestions, accuracy
    
    @handle_exceptions
    def getHomeworkStatistics(self):
        # Get number of homeworks completed
        query = "SELECT noHomeworksCompleted FROM statistic WHERE student_id = %s;"
        results = self.controller.database(query=query, parameter=(self.controller.user.user_id,), queryType="fetchItems")
        numHomeworksCompleted = results[0][0]

        # Get number of questions answered & correct
        query = """SELECT homework_accuracy.id, homework_accuracy.noQuestionsHomeworkAnswered, homework_accuracy.noCorrectHomeworkQuestions
        FROM homework_accuracy
        JOIN statistic_homework_accuracy ON homework_accuracy.id = statistic_homework_accuracy.homework_accuracy_id
        JOIN statistic ON statistic_homework_accuracy.statistic_id = statistic.id
        WHERE statistic.student_id = %s;"""
        
        results = self.controller.database(query=query, parameter=(self.controller.user.user_id,), queryType="fetchItems")
        numQuestionsAnswered = 0
        numCorrectQuestions = 0
        for result in results:
            numQuestionsAnswered += result[1]
            numCorrectQuestions += result[2]
        accuracy = (numCorrectQuestions / numQuestionsAnswered) * 100 if numQuestionsAnswered > 0 else 0

        return numHomeworksCompleted, numQuestionsAnswered, numCorrectQuestions, accuracy
    
    @handle_exceptions
    def getStrongestWeakestTopic(self):
        query = """SELECT topic_accuracy.topicCode, topic_accuracy.noQuestionsTopicAnswered, topic_accuracy.noCorrectTopicQuestions
        FROM topic_accuracy
        JOIN statistic_topic_accuracy ON topic_accuracy.id = statistic_topic_accuracy.topic_accuracy_id
        JOIN statistic ON statistic_topic_accuracy.statistic_id = statistic.id
        WHERE statistic.student_id = %s;"""

        results = self.controller.database(query=query, parameter=(self.controller.user.user_id,), queryType="fetchItems")
        topicAccuracies = []
        for result in results:
            topicCode = result[0]
            numQuestionsAnswered = result[1]
            numCorrectQuestions = result[2]
            accuracy = (numCorrectQuestions / numQuestionsAnswered) * 100 if numQuestionsAnswered > 0 else 0
            topicAccuracies.append((topicCode, accuracy))
        
        # Sort topics by accuracy
        topicAccuracies.sort(key=lambda x: x[1], reverse=True)
        return topicAccuracies[0], topicAccuracies[-1] # Return strongest and weakest topic as a tuple
    
    @handle_exceptions
    def accuracyLast10Homeworks(self):
        query = """SELECT homework.name, classes.name, homework_accuracy.noQuestionsHomeworkAnswered, homework_accuracy.noCorrectHomeworkQuestions
        FROM homework_accuracy
        JOIN statistic_homework_accuracy ON homework_accuracy.id = statistic_homework_accuracy.homework_accuracy_id
        JOIN statistic ON statistic_homework_accuracy.statistic_id = statistic.id
        JOIN homework ON homework.id = homework_accuracy.homework_id
        JOIN class_homework ON class_homework.homework_id = homework.id
        JOIN classes ON classes.id = class_homework.class_id
        WHERE statistic.student_id = %s
        ORDER BY homework_accuracy.id DESC
        LIMIT 10;"""

        results = self.controller.database(query=query, parameter=(self.controller.user.user_id,), queryType="fetchItems")
        accuracies = []
        for result in results:
            numQuestionsAnswered = result[2]
            numCorrectQuestions = result[3]
            accuracy = (numCorrectQuestions / numQuestionsAnswered) * 100 if numQuestionsAnswered > 0 else 0
            accuracies.append({
                "homeworkName": result[0],
                "className": result[1],
                "accuracy": accuracy
            })
        
        return accuracies
    
    @handle_exceptions
    def loadStatistics(self):
        # Question Stats
        questionStats = self.getQuestionStatistics()
        self.noQuestionsAnswered.setText(str(questionStats[0]))
        self.noQuestionsAnsweredCorrectly.setText(str(questionStats[1]))
        self.overallQuestionAccuracy.setText(f"{questionStats[2]:.2f}%")


        # Strongest & Weakest Topics
        strongest, weakest = self.getStrongestWeakestTopic()
        self.strongestTopic.setText(strongest[0])
        self.weakestTopic.setText(weakest[0])

        # Homework Stats
        homeworkStats = self.getHomeworkStatistics()
        self.noHomeworksCompleted.setText(str(homeworkStats[0]))
        self.homeworkAccuracy.setText(f"{homeworkStats[3]:.2f}%")
    
    @handle_exceptions
    def loadTopicAccuracy(self):
        # Get the topic statistics
        topic = self.chooseTopicComboBox.currentText()
        topicStats = self.getTopicStatistics(topic)
        self.topicAccuracy.setText(f"{topicStats[2]:.2f}%")
    
    @handle_exceptions
    def graphStatistics(self):
        # Get the chosen statistic to be graphed
        statisticToGraph = self.chooseGraphStatComboBox.currentText()
        if statisticToGraph == "Accuracy of the Last 10 Homeworks":
            # Line Plot (treat repeated homework names as separate points)
            data = self.accuracyLast10Homeworks()
            if not data:
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("No Data")
                dialogueBox.setText("No homework accuracy data available to plot.")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.exec()
                return

            # Ensure we only plot at most 10 most recent entries and show time order
            data = list(reversed(data))  # oldest -> newest left to right

            # Create x labels that keep duplicates distinct by prefixing an index
            x = [f"{i+1}. {item['homeworkName']} ({item['className']})" for i, item in enumerate(data)]
            y = [item['accuracy'] for item in data]

            # Create a figure and axis for a line plot
            self.figure = plt.figure()
            ax = self.figure.add_subplot(111)

            ax.plot(range(len(x)), y, marker='o', linestyle='-', color='tab:blue', alpha=1.0)
            ax.set_xticks(range(len(x))) 
            ax.set_xticklabels(x)
            ax.set_xlabel("Homework (Class)")
            ax.set_ylabel("Accuracy (%)")
            ax.set_title("Accuracy of Last 10 Homeworks")
            # Rotate x labels for readability
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')

            # Adjust layout to ensure x-labels are visible
            try:
                self.figure.tight_layout(rect=[0, 0.15, 1, 1])
            except Exception:
                self.figure.subplots_adjust(bottom=0.25)
        
        if statisticToGraph == "Topic Accuracy Bar Chart":
            # Bar chart of counts per topic: two bars per topic (answered, correct)
            topics = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "2.1", "2.2", "2.3", "2.4", "2.5"]
            counts = []
            for topic in topics:
                topicStats = self.getTopicStatistics(topic)
                counts.append((topicStats[0], topicStats[1]))  # (answered, correct)

            # Create a figure and axis for a grouped bar chart
            self.figure = plt.figure(figsize=(10, 5))
            ax = self.figure.add_subplot(111)

            x = np.arange(len(topics))
            totalAnswered = [c[0] for c in counts]
            totalCorrect = [c[1] for c in counts]

            width = 0.35
            bars1 = ax.bar(x - width/2, totalAnswered, width, label='Total Questions Answered', color='tab:blue')
            bars2 = ax.bar(x + width/2, totalCorrect, width, label='Questions Correctly Answered', color='tab:green')

            ax.set_xlabel("Topics")
            ax.set_ylabel("Number of Questions")
            ax.set_title("Topic Statistics")
            ax.set_xticks(x)
            ax.set_xticklabels(topics)
            ax.legend()

            # Annotate bar values for readability
            for bar in bars1 + bars2:
                height = bar.get_height()
                ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        
        if statisticToGraph == "Topic Accuracy Pie Chart":
            # Pie chart of overall accuracy per topic (only topics with >0 questions answered)
            topics = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "2.1", "2.2", "2.3", "2.4", "2.5"]
            accuracies = []
            labels = []
            for topic in topics:
                topicStats = self.getTopicStatistics(topic)
                if topicStats[0] > 0:  # Only include topics with >0 questions answered
                    accuracies.append(topicStats[2])  # accuracy
                    labels.append(topic)

            if not accuracies:
                dialogueBox = QMessageBox()
                dialogueBox.setWindowTitle("No Data")
                dialogueBox.setText("No topic accuracy data available to plot.")
                dialogueBox.setIcon(QMessageBox.Icon.Information)
                dialogueBox.exec()
                return

            # Create a figure and axis for a pie chart
            self.figure = plt.figure()
            ax = self.figure.add_subplot(111)

            # Reorder slices so 0.0% slices are not adjacent where possible
            pairs = list(zip(labels, accuracies))
            zeros = [p for p in pairs if p[1] == 0]
            nonzeros = [p for p in pairs if p[1] != 0]

            reordered = []
            # Alternate non-zero and zero entries to avoid adjacent zeros
            while nonzeros or zeros:
                if nonzeros:
                    reordered.append(nonzeros.pop(0))
                if zeros:
                    reordered.append(zeros.pop(0))

            # If interleaving produced no reorder (e.g., all nonzeros), fall back to original
            if reordered:
                labels, accuracies = zip(*reordered)
            else:
                labels = labels

            # Generate distinct colors for the (reordered) slices
            cmap = plt.get_cmap('tab20')
            colors = [cmap(i % cmap.N) for i in range(len(accuracies))]
            ax.pie(accuracies, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor': 'w'})
            ax.set_title("Overall Accuracy Distribution Across Topics")

        # Show Plot In Popup Window
        graphWindow = QDialog(self)
        graphWindow.setWindowTitle(statisticToGraph)
        layout = QVBoxLayout()
        canvas = FigureCanvas(self.figure)
        toolbar = NavigationToolbar(canvas, graphWindow)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        graphWindow.setLayout(layout)
        graphWindow.resize(900, 600)
        # Force a draw so layout/tight_layout take effect before showing
        try:
            canvas.draw()
        except Exception:
            pass
        graphWindow.exec()

