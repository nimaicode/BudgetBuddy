import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhD Finance Tracker Pro")
        self.setGeometry(100, 100, 800, 600)

        # Simple layout for demonstration
        layout = QVBoxLayout()  
        button = QPushButton("Click Me")
        layout.addWidget(button)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTracker()
    window.show()
    sys.exit(app.exec_())
