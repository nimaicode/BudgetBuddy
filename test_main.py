
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QInputDialog,
    QDialog,
    QHeaderView,
    QMessageBox,
    QTabWidget
)
from PyQt5.QtCore import QDate, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys

class EditTransactionDialog(QDialog):
    def __init__(self, row):
        super().__init__()
        self.setWindowTitle("Edit Transaction")
        self.layout = QVBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.fromString(row["Date"], "yyyy-MM-dd"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Income", "Expense"])
        self.type_combo.setCurrentText(row["Type"])
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Checking", "Savings", "Credit Card"])
        self.account_combo.setCurrentText(row["Account"])
        self.amount_edit = QLineEdit(str(row["Amount"]))
        self.source_category_edit = QLineEdit(row["Source/Category"])
        self.notes_edit = QLineEdit(row["Notes"])
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)

        self.layout.addWidget(QLabel("Date:"))
        self.layout.addWidget(self.date_edit)
        self.layout.addWidget(QLabel("Type:"))
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(QLabel("Account:"))
        self.layout.addWidget(self.account_combo)
        self.layout.addWidget(QLabel("Amount:"))
        self.layout.addWidget(self.amount_edit)
        self.layout.addWidget(QLabel("Source/Category:"))
        self.layout.addWidget(self.source_category_edit)
        self.layout.addWidget(QLabel("Notes:"))
        self.layout.addWidget(self.notes_edit)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def get_updated_data(self):
        return {
            "Date": self.date_edit.date().toString("yyyy-MM-dd"),
            "Type": self.type_combo.currentText(),
            "Account": self.account_combo.currentText(),
            "Amount": float(self.amount_edit.text()),
            "Source/Category": self.source_category_edit.text(),
            "Notes": self.notes_edit.text()
        }


class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
        self.setWindowTitle("PhD Finance Tracker Pro")
        self.setWindowIcon(QIcon('finance_icon.png'))
        self.layout = QVBoxLayout()
        self.init_ui()

        self.settings = QSettings("MyCompany", "FinanceTracker")
        
        # Load data is now manually triggered (only when needed)
        # No data loading here, it will be done later when the user interacts or views the data.

    def load_data(self):
        """
        Load data from CSV file if exists. 
        This function can be triggered later (e.g., when showing the table or at other user actions).
        """
        try:
            # Try to load the CSV file
            self.data = pd.read_csv("transactions.csv")
            
            # Validate the columns exist
            expected_columns = ["Date", "Type", "Account", "Amount", "Source/Category", "Notes"]
            if not set(expected_columns).issubset(self.data.columns):
                raise ValueError("The loaded data does not have the expected columns.")
            
            # Optionally, convert 'Date' to datetime and 'Amount' to numeric types for consistency
            self.data["Date"] = pd.to_datetime(self.data["Date"], errors='coerce')
            self.data["Amount"] = pd.to_numeric(self.data["Amount"], errors='coerce')
            
        except (FileNotFoundError, ValueError) as e:
            # If there's an error loading the file or it's malformed, create an empty DataFrame
            print(f"Error loading data: {e}")
            self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])

    def update_table(self, data=None):
        """
        Update the table widget with the provided data.
        If no data is provided, it will update with the current `self.data`.
        """
        if data is None:
            data = self.data

        self.table.setRowCount(len(data))
        for i, row in data.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(row["Date"].strftime('%Y-%m-%d') if isinstance(row["Date"], pd.Timestamp) else ''))
            self.table.setItem(i, 1, QTableWidgetItem(row["Type"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["Account"]))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row['Amount']:.2f}" if isinstance(row["Amount"], (float, int)) else ''))
            self.table.setItem(i, 4, QTableWidgetItem(row["Source/Category"]))
            self.table.setItem(i, 5, QTableWidgetItem(row["Notes"]))
        self.table.resizeColumnsToContents()

    def add_transaction(self):
        """
        Add a transaction to the table and the data.
        """
        # Collect the input data
        date = self.date_edit.date().toString("yyyy-MM-dd")
        _type = self.type_combo.currentText()
        account = self.account_combo.currentText()
        amount = float(self.amount_edit.text())
        source_category = self.source_category_edit.text()
        notes = self.notes_edit.text()

        # Create new row and append to the DataFrame
        new_row = pd.Series([date, _type, account, amount, source_category, notes], index=self.data.columns)
        self.data = self.data.append(new_row, ignore_index=True)
        self.save_data()
        
        # Update the table and charts
        self.update_table()
        self.update_analysis_charts()

        # Clear the input fields for the next transaction
        self.clear_input_fields()

    def save_data(self):
        """Save the current data to the CSV file."""
        self.data.to_csv("transactions.csv", index=False)

    def update_analysis_charts(self):
        """
        Update the analysis charts with the current data.
        Only call this method if the data has been modified.
        """
        # Make sure the data is valid before plotting
        valid_data = self.data.dropna(subset=["Amount"])  # Ensure Amount column is valid
        
        if valid_data.empty:
            print("No valid data to plot.")
        

        # Monthly Spending Bar Chart
        self.monthly_spending_figure.clear()
        ax = self.monthly_spending_figure.add_subplot(111)
        monthly_spending = valid_data[valid_data["Type"] == "Expense"].groupby(pd.Grouper(key="Date", freq="M"))["Amount"].sum()
        monthly_spending.plot(kind="bar", ax=ax)
        ax.set_title("Monthly Spending")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        self.monthly_spending_canvas.draw()

        # Category Pie Chart
        self.category_pie_figure.clear()
        ax = self.category_pie_figure.add_subplot(111)
        category_spending = valid_data[valid_data["Type"] == "Expense"].groupby("Source/Category")["Amount"].sum()
        category_spending.plot(kind="pie", ax=ax, autopct='%1.1f%%', startangle=90)
        ax.set_title("Expense Categories")
        self.category_pie_canvas.draw()

    def clear_input_fields(self):
        """Clear the input fields after adding a transaction."""
        self.date_edit.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)
        self.account_combo.setCurrentIndex(0)
        self.amount_edit.clear()
        self.source_category_edit.clear()
        self.notes_edit.clear()

    def load_settings(self):
        """Load window settings such as geometry."""
        window_geometry = self.settings.value("windowGeometry")
        if window_geometry:
            self.restoreGeometry(window_geometry)

    def closeEvent(self, event):
        """Save the window geometry before closing."""
        self.settings.setValue("windowGeometry", self.saveGeometry())
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    finance_tracker = FinanceTracker()
    finance_tracker.show()
    sys.exit(app.exec_())